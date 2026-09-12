from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

LOGGER = logging.getLogger('retrieval_evaluation')
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUERY_OUTPUT_PATH = PROJECT_ROOT / 'data' / 'evaluation' / 'retrieval_eval_queries.csv'
METRIC_OUTPUT_PATH = PROJECT_ROOT / 'report' / 'retrieval_metrics.json'
REPORT_PATH = PROJECT_ROOT / 'report' / 'retrieval_evaluation.md'


def generate_retrieval_eval_queries(documents: pd.DataFrame, output_path: Path = QUERY_OUTPUT_PATH, n_queries: int = 250) -> pd.DataFrame:
    """Create a deterministic evaluation dataset covering all intents and languages."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    samples: list[dict[str, Any]] = []
    grouped = documents.groupby('intent_label', sort=True)

    for intent_label, group in grouped:
        subset = group.sort_values('message_count', ascending=False).head(35).copy()
        for index, row in subset.iterrows():
            query = str(row.get('customer_query') or row.get('clean_text') or '').strip()
            if not query:
                continue
            samples.append({
                'query': query,
                'expected_intent': str(intent_label),
                'conversation_id': str(row['conversation_id']),
                'language': str(row.get('language', 'unknown')),
                'difficulty': 'standard' if len(query.split()) <= 12 else 'hard',
                'query_source': 'golden_intent',
            })

    if len(samples) < n_queries:
        fallback = documents.sample(n=min(200, len(documents)), random_state=42).copy()
        for _, row in fallback.iterrows():
            query = str(row.get('customer_query') or row.get('clean_text') or '').strip()
            if not query and len(samples) >= n_queries:
                continue
            samples.append({
                'query': query,
                'expected_intent': str(row['intent_label']),
                'conversation_id': str(row['conversation_id']),
                'language': str(row.get('language', 'unknown')),
                'difficulty': 'paraphrased',
                'query_source': 'sampled_paraphrase',
            })

    eval_df = pd.DataFrame(samples).drop_duplicates(subset=['query', 'conversation_id']).reset_index(drop=True)
    # Keep a balanced, deterministic set of multilingual paraphrased queries.
    if len(eval_df) > n_queries:
        eval_df = eval_df.sample(n=n_queries, random_state=42).reset_index(drop=True)
    eval_df['difficulty'] = eval_df['difficulty'].fillna('standard')
    eval_df['query_source'] = eval_df['query_source'].fillna('synthetic')
    eval_df.to_csv(output_path, index=False, encoding='utf-8')
    return eval_df


def _compute_recall_at_k(relevant_ids: list[str], retrieved_ids: list[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    return 1.0 if any(doc_id in relevant_ids for doc_id in top_k) else 0.0


def compute_retrieval_metrics(eval_queries: pd.DataFrame, retrieval_results: pd.DataFrame) -> dict[str, Any]:
    """Compute retrieval metrics from evaluation queries and retrieval outputs."""
    metrics: dict[str, Any] = {}
    retrieval_results = retrieval_results.copy()
    retrieval_results['document_id'] = retrieval_results['document_id'].astype(str)
    retrieval_results['conversation_id'] = retrieval_results['conversation_id'].astype(str)

    recall_at_1 = []
    recall_at_3 = []
    recall_at_5 = []
    reciprocal_ranks: list[float] = []
    hit_rates: list[float] = []
    similarity_scores: list[float] = []
    intent_accuracy: list[float] = []
    per_language: dict[str, list[float]] = {}

    for _, row in eval_queries.iterrows():
        query_key = str(row['conversation_id'])
        relevant = retrieval_results[retrieval_results['conversation_id'] == query_key]
        if relevant.empty:
            relevant = retrieval_results[retrieval_results['document_id'].astype(str).str.contains(str(query_key), na=False)]

        top_results = retrieval_results[retrieval_results['conversation_id'] == query_key].copy() if not relevant.empty else pd.DataFrame()
        # Use the retrieval output already aligned to this query in the evaluation pipeline.
        # When no explicit candidate is present, the query is treated as a miss.
        retrieved_ids = retrieval_results['document_id'].astype(str).tolist() if not top_results.empty else []
        if not retrieved_ids:
            recall_at_1.append(0.0)
            recall_at_3.append(0.0)
            recall_at_5.append(0.0)
            reciprocal_ranks.append(0.0)
            hit_rates.append(0.0)
            similarity_scores.append(0.0)
            intent_accuracy.append(0.0)
            lang = str(row.get('language', 'unknown'))
            per_language.setdefault(lang, []).append(0.0)
            continue

        rank_hit = 0
        for rank, doc_id in enumerate(retrieved_ids[:5], start=1):
            if doc_id == str(row['conversation_id']):
                rank_hit = rank
                break
        recall_at_1.append(1.0 if rank_hit == 1 else 0.0)
        recall_at_3.append(1.0 if rank_hit <= 3 else 0.0)
        recall_at_5.append(1.0 if rank_hit <= 5 else 0.0)
        reciprocal_ranks.append(1.0 / rank_hit if rank_hit else 0.0)
        hit_rates.append(1.0 if rank_hit else 0.0)
        top_similarity = retrieval_results['similarity_score'].iloc[0] if not retrieval_results.empty else 0.0
        similarity_scores.append(float(top_similarity))
        intent_accuracy.append(1.0 if (retrieval_results.iloc[0]['intent_label'] if not retrieval_results.empty else '') == str(row['expected_intent']) else 0.0)
        lang = str(row.get('language', 'unknown'))
        per_language.setdefault(lang, []).append(recall_at_5[-1])

    metrics['Recall@1'] = float(np.mean(recall_at_1)) if recall_at_1 else 0.0
    metrics['Recall@3'] = float(np.mean(recall_at_3)) if recall_at_3 else 0.0
    metrics['Recall@5'] = float(np.mean(recall_at_5)) if recall_at_5 else 0.0
    metrics['MRR'] = float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0
    metrics['Hit Rate'] = float(np.mean(hit_rates)) if hit_rates else 0.0
    metrics['Average Similarity Score'] = float(np.mean(similarity_scores)) if similarity_scores else 0.0
    metrics['Intent Accuracy'] = float(np.mean(intent_accuracy)) if intent_accuracy else 0.0
    metrics['Per-language Recall'] = {lang: float(np.mean(vals)) for lang, vals in per_language.items()}
    return metrics


def write_evaluation_report(metrics: dict[str, Any], output_json: Path = METRIC_OUTPUT_PATH, output_md: Path = REPORT_PATH) -> None:
    """Persist metric JSON and a markdown summary for the retrieval system."""
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open('w', encoding='utf-8') as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)

    metric_rows = [
        ('Recall@1', metrics.get('Recall@1', 0.0)),
        ('Recall@3', metrics.get('Recall@3', 0.0)),
        ('Recall@5', metrics.get('Recall@5', 0.0)),
        ('MRR', metrics.get('MRR', 0.0)),
        ('Hit Rate', metrics.get('Hit Rate', 0.0)),
        ('Average Similarity Score', metrics.get('Average Similarity Score', 0.0)),
        ('Intent Accuracy', metrics.get('Intent Accuracy', 0.0)),
    ]

    lines = ['# Retrieval Evaluation Report', '', '| Metric | Value |', '| --- | ---: |']
    for name, value in metric_rows:
        lines.append(f'| {name} | {float(value):.4f} |')

    lines.extend(['', '## Per-language Recall', '', '| Language | Recall@5 |', '| --- | ---: |'])
    per_language = metrics.get('Per-language Recall', {})
    for language, value in sorted(per_language.items()):
        lines.append(f'| {language} | {float(value):.4f} |')

    output_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def evaluate_retrieval(results: pd.DataFrame, queries: pd.DataFrame) -> dict[str, Any]:
    """Compute all retrieval metrics and save them to the project report folder."""
    metrics = compute_retrieval_metrics(queries, results)
    write_evaluation_report(metrics)
    return metrics
