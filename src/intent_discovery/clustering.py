from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def validate_embedding_array(embeddings: np.ndarray, expected_dim: int = 384) -> np.ndarray:
    arr = np.asarray(embeddings, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f'Embeddings must be 2D, got shape {arr.shape}')
    if arr.shape[1] != expected_dim:
        raise ValueError(f'Expected embedding dimension {expected_dim}, got {arr.shape[1]}')
    return arr


def reduce_dim(
    embeddings: np.ndarray,
    *,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    n_components: int = 2,
    metric: str = 'cosine',
    random_state: int = 42,
) -> np.ndarray:
    """Run UMAP to reduce embeddings to a 2D representation."""
    import umap

    emb = validate_embedding_array(embeddings)
    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        random_state=random_state,
    )
    reduced = reducer.fit_transform(emb)
    logger.info('UMAP reduction complete; output shape=%s', reduced.shape)
    return reduced.astype(np.float32)


def cluster_hdbscan(
    embeddings: np.ndarray,
    *,
    metric: str = 'euclidean',
    min_cluster_size: int = 25,
    min_samples: int = 10,
    cluster_selection_method: str = 'eom',
    prediction_data: bool = True,
) -> tuple[np.ndarray, np.ndarray, Any]:
    """Run HDBSCAN and return labels, probabilities, and clusterer."""
    import hdbscan

    emb = np.asarray(embeddings, dtype=np.float32)
    clusterer = hdbscan.HDBSCAN(
        metric=metric,
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_method=cluster_selection_method,
        prediction_data=prediction_data,
    )
    labels = clusterer.fit_predict(emb)
    probabilities = getattr(clusterer, 'probabilities_', np.ones(len(labels), dtype=float))
    logger.info('HDBSCAN produced %s clusters and %s noise points', len(set(labels) - {-1}), int((labels == -1).sum()))
    return labels.astype(int), np.asarray(probabilities, dtype=float), clusterer


def build_cluster_dataframe(metadata_path: Path, umap_embeddings: np.ndarray, labels: np.ndarray, probabilities: np.ndarray) -> pd.DataFrame:
    metadata_path = Path(metadata_path)
    metadata = pd.read_csv(metadata_path)
    if len(metadata) != len(labels):
        raise ValueError(f'Metadata rows ({len(metadata)}) do not match labels length ({len(labels)})')
    if len(umap_embeddings) != len(labels):
        raise ValueError(f'UMAP shape ({len(umap_embeddings)}) does not match labels length ({len(labels)})')

    result = metadata[['conversation_id']].copy()
    result['cluster_id'] = labels.astype(int)
    result['probability'] = probabilities.astype(float)
    result['is_noise'] = labels == -1
    result['umap_x'] = umap_embeddings[:, 0]
    result['umap_y'] = umap_embeddings[:, 1]
    return result


def compute_cluster_statistics(labels: np.ndarray) -> Dict[str, Any]:
    labels = np.asarray(labels)
    total = len(labels)
    noise_count = int((labels == -1).sum())
    non_noise = labels[labels != -1]
    unique_labels = np.unique(non_noise)
    sizes = {int(cluster): int((labels == cluster).sum()) for cluster in unique_labels}
    cluster_sizes = list(sizes.values())
    stats = {
        'total_conversations': int(total),
        'total_clusters': int(len(unique_labels)),
        'noise_count': noise_count,
        'noise_percentage': round((noise_count / total) * 100.0, 4) if total else 0.0,
        'cluster_sizes': sizes,
        'average_cluster_size': round(float(np.mean(cluster_sizes)) if cluster_sizes else 0.0, 4),
        'largest_cluster': int(max(cluster_sizes)) if cluster_sizes else 0,
        'smallest_cluster': int(min(cluster_sizes)) if cluster_sizes else 0,
    }
    return stats


def extract_top_terms_per_cluster(
    metadata_csv: Path,
    labels: np.ndarray,
    out_csv: Path,
    text_column: str = 'clean_text',
    top_n: int = 20,
) -> pd.DataFrame:
    """Extract top TF-IDF terms per cluster and save to CSV."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    metadata_csv = Path(metadata_csv)
    if not metadata_csv.exists():
        raise FileNotFoundError(metadata_csv)

    df = pd.read_csv(metadata_csv)
    if text_column not in df.columns:
        raise ValueError(f'Metadata CSV is missing required text column: {text_column}')

    labels = np.asarray(labels, dtype=int)
    rows: list[dict[str, Any]] = []

    for cluster_id in sorted(set(labels)):
        if cluster_id == -1:
            continue
        mask = labels == cluster_id
        if not np.any(mask):
            continue
        texts = df.loc[mask, text_column].fillna('').astype(str).tolist()
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=2000)
        matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        scores = np.asarray(matrix.mean(axis=0)).ravel()
        ranked_idx = np.argsort(scores)[::-1][:top_n]
        keywords = [feature_names[i] for i in ranked_idx if scores[i] > 0]

        rows.append(
            {
                'cluster_id': int(cluster_id),
                'top_keywords': ', '.join(keywords[:top_n]),
                'conversation_count': int(mask.sum()),
            }
        )

    out_df = pd.DataFrame(rows).sort_values('cluster_id').reset_index(drop=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_csv, index=False)
    logger.info('Saved cluster keyword summary to %s', out_csv)
    return out_df
