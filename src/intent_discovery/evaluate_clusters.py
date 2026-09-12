from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_cluster_metrics(embeddings: np.ndarray, labels: np.ndarray, *, noise_label: int = -1) -> Dict[str, Any]:
    emb = np.asarray(embeddings, dtype=np.float32)
    labels = np.asarray(labels, dtype=int)
    valid_mask = labels != noise_label
    valid_emb = emb[valid_mask]
    valid_labels = labels[valid_mask]

    metrics: Dict[str, Any] = {
        'total_conversations': int(len(labels)),
        'noise_points': int((labels == noise_label).sum()),
        'noise_percentage': round(float((labels == noise_label).mean() * 100.0), 4),
        'number_of_clusters': int(len(np.unique(valid_labels))),
        'silhouette_score': None,
        'davies_bouldin_index': None,
        'calinski_harabasz_score': None,
    }

    if len(np.unique(valid_labels)) < 2:
        return metrics

    from sklearn import metrics as sk_metrics

    try:
        metrics['silhouette_score'] = float(sk_metrics.silhouette_score(valid_emb, valid_labels))
    except Exception:
        metrics['silhouette_score'] = None
    try:
        metrics['davies_bouldin_index'] = float(sk_metrics.davies_bouldin_score(valid_emb, valid_labels))
    except Exception:
        metrics['davies_bouldin_index'] = None
    try:
        metrics['calinski_harabasz_score'] = float(sk_metrics.calinski_harabasz_score(valid_emb, valid_labels))
    except Exception:
        metrics['calinski_harabasz_score'] = None

    return metrics


def generate_cluster_quality_report(metrics: Dict[str, Any], out_md: Path) -> None:
    out_md = Path(out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    silhouette = metrics.get('silhouette_score')
    dbi = metrics.get('davies_bouldin_index')
    ch = metrics.get('calinski_harabasz_score')
    noise_pct = metrics.get('noise_percentage', 0.0)
    n_clusters = metrics.get('number_of_clusters', 0)

    def interpret_silhouette(value):
        if value is None:
            return 'Not available because the cluster set is too small.'
        if value > 0.5:
            return 'Strong cluster separation; the semantic intent groups are well defined.'
        if value > 0.25:
            return 'Moderate separation; the clusters are usable but some intent boundaries overlap.'
        return 'Weak separation; semantically similar intents may be merging together.'

    def interpret_dbi(value):
        if value is None:
            return 'Not available because the cluster set is too small.'
        if value < 1:
            return 'Excellent compactness and separation between clusters.'
        if value < 2:
            return 'Reasonable cluster structure with some overlap.'
        return 'Clusters are relatively diffuse and may need parameter tuning.'

    def interpret_ch(value):
        if value is None:
            return 'Not available because the cluster set is too small.'
        if value > 1000:
            return 'Very strong cluster structure and high between-cluster variance.'
        if value > 200:
            return 'Stable cluster structure with moderate discrimination.'
        return 'Cluster separation is limited and may benefit from tuning.'

    lines = [
        '# Cluster Quality Report',
        '',
        '## Summary',
        f'- Number of non-noise clusters: {n_clusters}',
        f'- Noise percentage: {noise_pct:.2f}%',
        f'- Silhouette score: {silhouette:.4f}' if silhouette is not None else '- Silhouette score: N/A',
        f'- Davies-Bouldin index: {dbi:.4f}' if dbi is not None else '- Davies-Bouldin index: N/A',
        f'- Calinski-Harabasz score: {ch:.4f}' if ch is not None else '- Calinski-Harabasz score: N/A',
        '',
        '## Interpretation',
        '',
        f'### Silhouette Score\n{interpret_silhouette(silhouette)}',
        '',
        f'### Davies-Bouldin Index\n{interpret_dbi(dbi)}',
        '',
        f'### Calinski-Harabasz Score\n{interpret_ch(ch)}',
        '',
        f'### Noise Analysis\nNoise accounts for {noise_pct:.2f}% of the conversations. This is acceptable for semantic clustering when ambiguous or low-confidence conversations are treated as outliers.',
    ]
    out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    logger.info('Saved cluster quality report to %s', out_md)


def validate_outputs(embeddings_npy: Path, metadata_csv: Path, labels: Iterable[int], required_files: Iterable[Path]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    embeddings_npy = Path(embeddings_npy)
    metadata_csv = Path(metadata_csv)

    summary['embeddings_exists'] = embeddings_npy.exists()
    summary['metadata_exists'] = metadata_csv.exists()
    summary['embeddings_shape'] = None
    summary['metadata_rows'] = 0

    if summary['embeddings_exists']:
        arr = np.load(embeddings_npy)
        summary['embeddings_shape'] = tuple(arr.shape)
    if summary['metadata_exists']:
        summary['metadata_rows'] = len(pd.read_csv(metadata_csv))

    labels_list = list(labels)
    summary['labels_length'] = len(labels_list)

    file_checks = {}
    missing = []
    for p in required_files:
        p = Path(p)
        exists = p.exists()
        file_checks[str(p)] = exists
        if not exists:
            missing.append(str(p))
    summary['file_checks'] = file_checks
    summary['missing_files'] = missing

    ok = True
    if not summary['embeddings_exists'] or summary['metadata_rows'] == 0:
        ok = False
    if summary['embeddings_shape'] and summary['metadata_rows'] and summary['embeddings_shape'][0] != summary['metadata_rows']:
        ok = False
    if summary['labels_length'] != summary['metadata_rows']:
        ok = False
    if missing:
        ok = False

    summary['overall_pass'] = bool(ok)
    print('=== Validation Summary ===')
    print('Embeddings exists:', summary['embeddings_exists'])
    print('Metadata rows:', summary['metadata_rows'])
    print('Embeddings shape:', summary['embeddings_shape'])
    print('Labels length:', summary['labels_length'])
    for path, exists in file_checks.items():
        print(f'{path}: {exists}')
    print('Overall:', 'PASS' if ok else 'FAIL')
    return summary


def save_cluster_evaluation(metrics: dict[str, Any], out_json: Path) -> None:
    out_json = Path(out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    logger.info('Saved cluster evaluation JSON to %s', out_json)
