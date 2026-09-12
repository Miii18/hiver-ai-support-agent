from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


def generate_intent_summary(
    metadata_csv: Path,
    labels: Iterable[int],
    out_csv: Path,
    out_md: Path,
    text_column: str = 'clean_text',
) -> pd.DataFrame:
    metadata_csv = Path(metadata_csv)
    if not metadata_csv.exists():
        raise FileNotFoundError(metadata_csv)

    df = pd.read_csv(metadata_csv)
    if text_column not in df.columns:
        raise ValueError(f'Metadata CSV is missing required text column: {text_column}')

    labels = list(labels)
    if len(labels) != len(df):
        raise ValueError(f'Labels length {len(labels)} does not match metadata rows {len(df)}')

    df = df.copy()
    df['cluster_id'] = labels

    rows = []
    for cluster_id in sorted(set(labels)):
        if cluster_id == -1:
            continue
        subset = df[df['cluster_id'] == cluster_id].copy()
        texts = subset[text_column].fillna('').astype(str).tolist()
        if not texts:
            continue

        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=20)
        matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        scores = matrix.mean(axis=0).A1
        ranked = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)[:20]
        top_keywords = ', '.join([name for name, _ in ranked if name])

        if not ranked:
            intent_label = f'Cluster {cluster_id}'
            confidence = 0.0
        else:
            stemmed = [name.replace('_', ' ').title() for name, _ in ranked[:3]]
            intent_label = ' '.join(stemmed) if stemmed else f'Cluster {cluster_id}'
            confidence = round(float(sum(score for _, score in ranked[:10]) / max(len(ranked[:10]), 1)), 4)

        representative = subset.sort_values('message_count', ascending=False).head(3)
        rows.append(
            {
                'cluster_id': int(cluster_id),
                'intent_label': intent_label,
                'top_keywords': top_keywords,
                'conversation_count': int(len(subset)),
                'confidence': float(confidence),
                'representative_conversations': '\n---\n'.join(
                    (row.get(text_column, '')[:400] if isinstance(row.get(text_column, ''), str) else str(row.get(text_column, '')))
                    for _, row in representative.iterrows()
                ),
            }
        )

    summary_df = pd.DataFrame(rows).sort_values('cluster_id').reset_index(drop=True)
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(out_csv, index=False)

    out_md = Path(out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open('w', encoding='utf-8') as f:
        f.write('# Semantic Intent Summary\n\n')
        f.write('This summary captures the dominant themes in each discovered semantic cluster using TF-IDF keyword extraction and representative conversations.\n\n')
        for _, row in summary_df.iterrows():
            f.write(f"## Cluster {int(row['cluster_id'])}\n\n")
            f.write(f"- Intent label: **{row['intent_label']}**\n")
            f.write(f"- Conversation count: {int(row['conversation_count'])}\n")
            f.write(f"- Confidence: {float(row['confidence']):.4f}\n")
            f.write(f"- Top keywords: {row['top_keywords']}\n\n")
            rep_text = row.get('representative_conversations', '')
            if rep_text:
                f.write('Representative conversations:\n\n')
                for chunk in rep_text.split('\n---\n'):
                    f.write(f'- {chunk[:400]}\n')
                f.write('\n')

    logger.info('Saved semantic intent summary CSV and markdown to %s and %s', out_csv, out_md)
    return summary_df.drop(columns=['representative_conversations'])


def generate_intent_report(metadata_csv: Path, labels: Iterable[int], top_terms_csv: Path, out_md: Path, examples_per_cluster: int = 3) -> None:
    metadata_csv = Path(metadata_csv)
    top_terms_csv = Path(top_terms_csv)
    out_md = Path(out_md)
    if not metadata_csv.exists():
        raise FileNotFoundError(metadata_csv)
    df = pd.read_csv(metadata_csv)
    labels = list(labels)
    if len(labels) != len(df):
        raise ValueError('Labels length must match metadata rows')

    df = df.copy()
    df['cluster_id'] = labels
    top_df = pd.read_csv(top_terms_csv)

    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open('w', encoding='utf-8') as f:
        f.write('# Semantic Intent Discovery Report\n\n')
        f.write('This report contains the semantically interpreted cluster themes, representative conversations, and topic summaries for the Phase 4 intent discovery pipeline.\n\n')
        for cluster_id in sorted(set(labels)):
            if cluster_id == -1:
                continue
            cluster_meta = top_df[top_df['cluster_id'] == cluster_id] if 'cluster_id' in top_df.columns else pd.DataFrame()
            if cluster_meta.empty:
                continue
            row = cluster_meta.iloc[0]
            f.write(f'## Cluster {int(cluster_id)}\n\n')
            f.write(f'- Top keywords: {row.get("top_keywords", "")}\n')
            f.write(f'- Conversation count: {int((df["cluster_id"] == cluster_id).sum())}\n\n')
            examples = df[df['cluster_id'] == cluster_id].sort_values('message_count', ascending=False).head(examples_per_cluster)
            if examples.empty:
                f.write('_No representative conversations available._\n\n')
                continue
            f.write('Representative conversations:\n\n')
            for _, example in examples.iterrows():
                text = str(example.get('clean_text', ''))
                if len(text) > 400:
                    text = text[:400] + '...'
                f.write(f'- {text}\n')
            f.write('\n')
    logger.info('Saved semantic intent markdown report to %s', out_md)
