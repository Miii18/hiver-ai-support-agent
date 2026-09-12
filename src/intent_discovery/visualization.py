from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

logger = logging.getLogger(__name__)


def _cluster_color(label: int, default_palette: list[str] | None = None) -> str:
    if label == -1:
        return 'lightgray'
    palette = default_palette or ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    return palette[int(label) % len(palette)]


def plot_umap_clusters(umap_coords: np.ndarray, labels: np.ndarray, out_path: Path) -> None:
    umap_coords = np.asarray(umap_coords, dtype=np.float32)
    labels = np.asarray(labels, dtype=int)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    unique_labels = sorted(set(labels.tolist()))
    for label in unique_labels:
        mask = labels == label
        color = _cluster_color(label)
        ax.scatter(umap_coords[mask, 0], umap_coords[mask, 1], s=10, c=color, alpha=0.8, label=('Noise' if label == -1 else f'Cluster {label}'))
    ax.set_title('UMAP projection of semantic clusters')
    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    ax.legend(title='Cluster', bbox_to_anchor=(1.04, 1), loc='upper left')
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    logger.info('Saved UMAP cluster plot to %s', out_path)


def plot_cluster_size_distribution(labels: np.ndarray, out_path: Path) -> None:
    labels = np.asarray(labels, dtype=int)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = pd.Series(labels).value_counts().sort_index()
    if -1 in counts.index:
        counts = counts.drop(-1, errors='ignore')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(counts.index.astype(str), counts.values, color='#4c72b0')
    ax.set_title('Cluster size distribution')
    ax.set_xlabel('Cluster ID')
    ax.set_ylabel('Conversation count')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    logger.info('Saved cluster size distribution plot to %s', out_path)


def plot_noise_distribution(labels: np.ndarray, out_path: Path) -> None:
    labels = np.asarray(labels, dtype=int)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {'Clustered': int((labels != -1).sum()), 'Noise': int((labels == -1).sum())}
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(counts.values(), labels=[f'{k} ({v})' for k, v in counts.items()], autopct='%1.1f%%', startangle=90, colors=['#4C78A8', '#B0B0B0'])
    ax.set_title('Noise vs cluster assignments')
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    logger.info('Saved noise distribution plot to %s', out_path)


def plot_top_clusters(labels: np.ndarray, out_path: Path, top_n: int = 15) -> None:
    labels = np.asarray(labels, dtype=int)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = pd.Series(labels).value_counts().sort_values(ascending=False)
    counts = counts[counts.index != -1].head(top_n)
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.bar(counts.index.astype(str), counts.values, color='#2ca02c')
    ax.set_title(f'Top {min(top_n, len(counts))} largest intent clusters')
    ax.set_xlabel('Cluster ID')
    ax.set_ylabel('Conversation count')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    logger.info('Saved top cluster plot to %s', out_path)


def plot_interactive_umap(umap_coords: np.ndarray, labels: np.ndarray, out_path: Path) -> None:
    umap_coords = np.asarray(umap_coords, dtype=np.float32)
    labels = np.asarray(labels, dtype=int)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame({'umap_x': umap_coords[:, 0], 'umap_y': umap_coords[:, 1], 'cluster_id': labels})
    fig = px.scatter(
        df,
        x='umap_x',
        y='umap_y',
        color=df['cluster_id'].map(lambda v: 'noise' if v == -1 else f'cluster_{v}'),
        title='Interactive UMAP clustering visualization',
        color_discrete_sequence=['#b0b0b0'] + [
            '#%02x%02x%02x' % (((i * 53) % 256), ((i * 91) % 256), ((i * 157) % 256))
            for i in range(20)
        ],
        opacity=0.7,
    )
    fig.update_traces(marker={'size': 5})
    fig.write_html(out_path)
    logger.info('Saved interactive UMAP HTML to %s', out_path)
