"""Run the Phase 4 semantic intent discovery pipeline end-to-end.

Usage:
    python scripts/run_phase4.py
    python scripts/run_phase4.py --force
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.intent_discovery.clustering import (
    build_cluster_dataframe,
    cluster_hdbscan,
    compute_cluster_statistics,
    extract_top_terms_per_cluster,
    reduce_dim,
)
from src.intent_discovery.evaluate_clusters import (
    compute_cluster_metrics,
    generate_cluster_quality_report,
    save_cluster_evaluation,
    validate_outputs,
)
from src.intent_discovery.intent_summary import generate_intent_summary
from src.intent_discovery.visualization import (
    plot_cluster_size_distribution,
    plot_interactive_umap,
    plot_noise_distribution,
    plot_top_clusters,
    plot_umap_clusters,
)

LOGGER = logging.getLogger('phase4')


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        Path(path).parent.mkdir(parents=True, exist_ok=True)


def run(force: bool = False) -> int:
    start = time.time()
    root = PROJECT_ROOT
    embeddings_path = root / 'data' / 'embeddings' / 'sample_sentence_embeddings.npy'
    metadata_path = root / 'data' / 'embeddings' / 'sample_metadata.csv'
    clusters_dir = root / 'data' / 'clusters'
    report_dir = root / 'report'
    assets_dir = root / 'assets' / 'clustering'

    ensure_dirs([
        clusters_dir / 'umap_embeddings.npy',
        clusters_dir / 'umap_coordinates.csv',
        clusters_dir / 'hdbscan_labels.csv',
        clusters_dir / 'intent_summary.csv',
        report_dir / 'cluster_statistics.json',
        report_dir / 'cluster_evaluation.json',
        report_dir / 'cluster_quality_report.md',
        report_dir / 'semantic_intent_summary.md',
        assets_dir / 'umap_clusters.png',
    ])

    LOGGER.info('Phase 4 pipeline starting for project at %s', root)

    if not embeddings_path.exists():
        raise FileNotFoundError(f'Missing required embeddings file: {embeddings_path}')

    embeddings = np.load(embeddings_path)
    if embeddings.ndim != 2 or embeddings.shape[1] != 384:
        raise ValueError(f'Embedding file should be 2D with 384 columns; got {embeddings.shape}')

    if not metadata_path.exists():
        raise FileNotFoundError(f'Missing required metadata file: {metadata_path}')
    metadata = pd.read_csv(metadata_path)
    if len(metadata) != len(embeddings):
        raise ValueError(f'Metadata length {len(metadata)} does not match embeddings length {len(embeddings)}')

    umap_output = clusters_dir / 'umap_embeddings.npy'
    umap_csv = clusters_dir / 'umap_coordinates.csv'
    labels_csv = clusters_dir / 'hdbscan_labels.csv'
    intent_csv = clusters_dir / 'intent_summary.csv'
    cluster_stats_path = report_dir / 'cluster_statistics.json'
    cluster_eval_path = report_dir / 'cluster_evaluation.json'
    cluster_report_path = report_dir / 'cluster_quality_report.md'
    semantic_report_path = report_dir / 'semantic_intent_summary.md'

    # UMAP
    if not umap_output.exists() or force:
        LOGGER.info('Running UMAP reduction')
        umap_embeddings = reduce_dim(
            embeddings,
            n_neighbors=15,
            min_dist=0.1,
            n_components=2,
            metric='cosine',
            random_state=42,
        )
        np.save(umap_output, umap_embeddings.astype(np.float32))
    else:
        LOGGER.info('Loading existing UMAP embeddings from %s', umap_output)
        umap_embeddings = np.load(umap_output)

    umap_df = pd.DataFrame({
        'conversation_id': metadata['conversation_id'],
        'umap_x': umap_embeddings[:, 0],
        'umap_y': umap_embeddings[:, 1],
    })
    if not umap_csv.exists() or force:
        umap_df.to_csv(umap_csv, index=False)
    else:
        LOGGER.info('Using existing UMAP coordinates at %s', umap_csv)

    # HDBSCAN
    if not labels_csv.exists() or force:
        LOGGER.info('Running HDBSCAN clustering')
        labels, probabilities, _ = cluster_hdbscan(
            umap_embeddings,
            metric='euclidean',
            min_cluster_size=25,
            min_samples=10,
            cluster_selection_method='eom',
            prediction_data=True,
        )

        labels_df = build_cluster_dataframe(metadata_path, umap_embeddings, labels, probabilities)
        labels_df[['conversation_id', 'cluster_id', 'probability', 'is_noise']].to_csv(labels_csv, index=False)
    else:
        LOGGER.info('Loading existing HDBSCAN labels from %s', labels_csv)
        labels_df = pd.read_csv(labels_csv)
        labels = labels_df['cluster_id'].to_numpy(dtype=int)
        probabilities = labels_df['probability'].to_numpy(float)

    # Cluster stats
    stats = compute_cluster_statistics(labels)
    if not cluster_stats_path.exists() or force:
        cluster_stats_path.parent.mkdir(parents=True, exist_ok=True)
        cluster_stats_path.write_text(json.dumps(stats, indent=2), encoding='utf-8')
    else:
        LOGGER.info('Using existing cluster statistics file %s', cluster_stats_path)

    # Evaluation
    metrics = compute_cluster_metrics(embeddings, labels)
    if not cluster_eval_path.exists() or force:
        save_cluster_evaluation(metrics, cluster_eval_path)
    else:
        LOGGER.info('Using existing cluster evaluation file %s', cluster_eval_path)

    if not cluster_report_path.exists() or force:
        generate_cluster_quality_report(metrics, cluster_report_path)

    # Intent summary
    if not intent_csv.exists() or force:
        LOGGER.info('Generating intent summary output')
        top_keywords_path = clusters_dir / 'top_keywords.csv'
        keyword_summary = extract_top_terms_per_cluster(metadata_path, labels, top_keywords_path, text_column='clean_text', top_n=20)
        summary_df = generate_intent_summary(metadata_path, labels, intent_csv, semantic_report_path, text_column='clean_text')
        if summary_df.empty:
            raise RuntimeError('No semantic clusters were discovered; check clustering configuration.')
        if 'cluster_id' in keyword_summary.columns:
            merged = summary_df.merge(keyword_summary[['cluster_id', 'top_keywords']], on='cluster_id', how='left')
            merged['top_keywords'] = merged['top_keywords_y'].fillna(merged['top_keywords_x'])
            merged = merged.drop(columns=[c for c in ['top_keywords_x','top_keywords_y'] if c in merged.columns])
            merged = merged[['cluster_id', 'intent_label', 'top_keywords', 'conversation_count', 'confidence']]
            merged.to_csv(intent_csv, index=False)
    else:
        LOGGER.info('Using existing intent summary CSV at %s', intent_csv)

    # Visualization
    plots = [
        (assets_dir / 'umap_clusters.png', lambda: plot_umap_clusters(umap_embeddings, labels, assets_dir / 'umap_clusters.png')),
        (assets_dir / 'cluster_size_distribution.png', lambda: plot_cluster_size_distribution(labels, assets_dir / 'cluster_size_distribution.png')),
        (assets_dir / 'noise_distribution.png', lambda: plot_noise_distribution(labels, assets_dir / 'noise_distribution.png')),
        (assets_dir / 'top_clusters.png', lambda: plot_top_clusters(labels, assets_dir / 'top_clusters.png', top_n=15)),
        (assets_dir / 'interactive_umap.html', lambda: plot_interactive_umap(umap_embeddings, labels, assets_dir / 'interactive_umap.html')),
    ]
    for path, fn in plots:
        if not path.exists() or force:
            fn()

    # Validation
    required = [
        embeddings_path,
        umap_output,
        umap_csv,
        labels_csv,
        intent_csv,
        cluster_stats_path,
        cluster_eval_path,
        cluster_report_path,
        semantic_report_path,
        assets_dir / 'umap_clusters.png',
        assets_dir / 'cluster_size_distribution.png',
        assets_dir / 'noise_distribution.png',
        assets_dir / 'top_clusters.png',
        assets_dir / 'interactive_umap.html',
    ]
    validation_summary = validate_outputs(embeddings_path, metadata_path, labels, required)

    elapsed = time.time() - start
    total_clusters = int(stats['total_clusters'])
    noise_percentage = stats['noise_percentage']
    passed = bool(validation_summary.get('overall_pass'))

    banner = '# ======================================================'
    print(banner)
    print('PHASE 4 COMPLETED SUCCESSFULLY')
    print(f'Total conversations clustered: {len(embeddings):,}')
    print(f'Total semantic clusters: {total_clusters}')
    print(f'Noise percentage: {noise_percentage:.2f}%')
    print(f'Silhouette score: {metrics.get("silhouette_score") if metrics.get("silhouette_score") is not None else "N/A"}')
    print(f'Davies-Bouldin index: {metrics.get("davies_bouldin_index") if metrics.get("davies_bouldin_index") is not None else "N/A"}')
    print(f'Calinski-Harabasz score: {metrics.get("calinski_harabasz_score") if metrics.get("calinski_harabasz_score") is not None else "N/A"}')
    print(f'Generated artifacts count: {sum(1 for x in required if Path(x).exists())}')
    print(f'Execution time: {elapsed:.2f} seconds')

    if not passed:
        print('Validation summary: FAIL')
        return 1
    print('Validation summary: PASS')
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the Phase 4 semantic intent discovery pipeline.')
    parser.add_argument('--force', action='store_true', help='Overwrite existing Phase 4 artifacts.')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    args = parse_args()
    sys.exit(run(force=args.force))
