from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

EMBEDDINGS = ROOT / 'data' / 'embeddings' / 'sample_sentence_embeddings.npy'
UMAP_EMBEDDINGS = ROOT / 'data' / 'clusters' / 'umap_embeddings.npy'
UMAP_COORDS = ROOT / 'data' / 'clusters' / 'umap_coordinates.csv'
HDBSCAN_LABELS = ROOT / 'data' / 'clusters' / 'hdbscan_labels.csv'
INTENT_SUMMARY = ROOT / 'data' / 'clusters' / 'intent_summary.csv'
CLUSTER_STATS = ROOT / 'report' / 'cluster_statistics.json'
CLUSTER_EVAL = ROOT / 'report' / 'cluster_evaluation.json'
QUALITY_REPORT = ROOT / 'report' / 'cluster_quality_report.md'
SEMANTIC_REPORT = ROOT / 'report' / 'semantic_intent_summary.md'
VISUALS = [
    ROOT / 'assets' / 'clustering' / 'umap_clusters.png',
    ROOT / 'assets' / 'clustering' / 'cluster_size_distribution.png',
    ROOT / 'assets' / 'clustering' / 'noise_distribution.png',
    ROOT / 'assets' / 'clustering' / 'top_clusters.png',
    ROOT / 'assets' / 'clustering' / 'interactive_umap.html',
]


def test_embedding_shape() -> None:
    arr = np.load(EMBEDDINGS)
    assert arr.shape == (10000, 384), arr.shape


def test_umap_outputs() -> None:
    umap_arr = np.load(UMAP_EMBEDDINGS)
    assert umap_arr.shape[0] == 10000
    assert umap_arr.shape[1] == 2

    coords = pd.read_csv(UMAP_COORDS)
    assert {'conversation_id', 'umap_x', 'umap_y'}.issubset(coords.columns)
    assert len(coords) == 10000


def test_hdbscan_and_summary_outputs() -> None:
    labels = pd.read_csv(HDBSCAN_LABELS)
    assert {'conversation_id', 'cluster_id', 'probability', 'is_noise'}.issubset(labels.columns)
    assert len(labels) == 10000

    intent = pd.read_csv(INTENT_SUMMARY)
    assert {'cluster_id', 'intent_label', 'top_keywords', 'conversation_count', 'confidence'}.issubset(intent.columns)
    assert len(intent) > 0


def test_reports_exist() -> None:
    for p in [CLUSTER_STATS, CLUSTER_EVAL, QUALITY_REPORT, SEMANTIC_REPORT]:
        assert p.exists(), f'Missing {p}'

    stats = json.loads(CLUSTER_STATS.read_text(encoding='utf-8'))
    assert 'total_clusters' in stats
    assert 'noise_percentage' in stats

    eval_data = json.loads(CLUSTER_EVAL.read_text(encoding='utf-8'))
    assert 'silhouette_score' in eval_data or 'noise_percentage' in eval_data


def test_visualizations_exist() -> None:
    for p in VISUALS:
        assert p.exists(), f'Missing {p}'
