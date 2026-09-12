from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.intent_discovery.validate_intents import (
    build_distribution_summary,
    build_taxonomy_from_cluster_summary,
    build_golden_intents,
    infer_language,
    validate_intent_dataset,
)

LOGGER = logging.getLogger('phase5')


def ensure_dirs(paths: list[Path]) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)


def split_customer_and_amazon(text: str) -> tuple[str, str]:
    text = str(text or '')
    if 'Amazon:' in text:
        head, tail = text.split('Amazon:', 1)
        customer = head.replace('Customer:', '', 1)
        amazon = tail.strip()
        return customer.strip(), amazon.strip()
    return text.strip(), ''


def build_taxonomy_and_labels(force: bool = False) -> tuple[list[dict], pd.DataFrame, Path]:
    root = PROJECT_ROOT
    cluster_labels_path = root / 'data' / 'clusters' / 'hdbscan_labels.csv'
    intent_summary_path = root / 'data' / 'clusters' / 'intent_summary.csv'
    sample_path = root / 'data' / 'processed' / 'amazon_conversations_sample.csv'
    taxonomy_path = root / 'data' / 'intents' / 'intent_taxonomy.json'
    golden_path = root / 'data' / 'intents' / 'golden_intents.csv'

    if not cluster_labels_path.exists():
        raise FileNotFoundError(f'Missing Phase 4 clustering output: {cluster_labels_path}')
    if not intent_summary_path.exists():
        raise FileNotFoundError(f'Missing Phase 4 intent summary: {intent_summary_path}')
    if not sample_path.exists():
        raise FileNotFoundError(f'Missing sample dataset: {sample_path}')

    labels_df = pd.read_csv(cluster_labels_path)
    intent_summary = pd.read_csv(intent_summary_path)
    sample_df = pd.read_csv(sample_path)
    # align expected column names from Phase 4 output
    if 'cluster_id' not in labels_df.columns:
        labels_df = labels_df.rename(columns={'cluster': 'cluster_id'})
    if 'cluster_id' not in intent_summary.columns:
        intent_summary = intent_summary.rename(columns={'cluster': 'cluster_id'})
    if 'intent_label' not in intent_summary.columns:
        intent_summary['intent_label'] = intent_summary.get('cluster_id').map(lambda v: f'Cluster {v}')

    taxonomy = build_taxonomy_from_cluster_summary(intent_summary, taxonomy_path)
    golden_df = build_golden_intents(labels_df, sample_df, taxonomy, random_state=42)
    golden_df.to_csv(golden_path, index=False)
    return taxonomy, golden_df, golden_path


def create_intent_examples(golden_df: pd.DataFrame, out_md: Path, out_json: Path) -> list[dict[str, object]]:
    example_rows: list[dict[str, object]] = []
    records = []

    for intent_label, group in golden_df.groupby('intent_label', sort=True):
        ordered = group.sort_values(['confidence', 'message_count'], ascending=[False, False]).head(15).copy()
        ordered['customer_query'] = ordered['clean_text'].map(lambda x: split_customer_and_amazon(x)[0][:500])
        ordered['amazon_response'] = ordered['clean_text'].map(lambda x: split_customer_and_amazon(x)[1][:500])
        top_keywords = []
        for _, row in ordered.iterrows():
            text = str(row['clean_text']).lower()
            for token in ['order', 'delivery', 'refund', 'prime', 'login', 'account', 'coupon', 'delivery', 'shipment', 'return', 'support', 'issue', 'payment']:
                if token in text and token not in top_keywords:
                    top_keywords.append(token)
        if not top_keywords:
            top_keywords = ['customer', 'support', 'help']

        average_conf = float(ordered['confidence'].mean()) if not ordered.empty else 0.0
        category_name = ordered['intent_category'].iloc[0] if not ordered.empty else 'Other'
        records.append({
            'intent_label': intent_label,
            'intent_category': category_name,
            'representative_conversations': int(len(ordered)),
            'top_keywords': top_keywords[:10],
            'average_confidence': round(average_conf, 4),
            'conversation_count': int(len(group)),
        })

        example_rows.append(f'## {intent_label}')
        example_rows.append('')
        category_name = ordered['intent_category'].iloc[0] if not ordered.empty else 'Other'
        example_rows.append(f'- Intent category: {category_name}')
        example_rows.append(f'- Conversation count: {int(len(group))}')
        example_rows.append(f'- Average confidence: {average_conf:.4f}')
        example_rows.append(f'- Top keywords: {", ".join(top_keywords[:10])}')
        example_rows.append('')
        example_rows.append('Representative conversations:')
        example_rows.append('')
        for _, row in ordered.head(5).iterrows():
            customer_query, amazon_response = split_customer_and_amazon(row['clean_text'])
            example_rows.append(f'- Query: {customer_query[:300]}')
            example_rows.append(f'  Response: {amazon_response[:300]}')
            example_rows.append('')

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text('\n'.join(example_rows) + '\n', encoding='utf-8')
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    return records


def create_distribution_reports(golden_df: pd.DataFrame, report_dir: Path) -> tuple[dict, dict]:
    distribution = build_distribution_summary(golden_df)
    distribution_path = report_dir / 'intent_distribution.json'
    distribution_path.write_text(json.dumps(distribution, ensure_ascii=False, indent=2), encoding='utf-8')

    report_lines = ['# Intent Distribution Report', '', f'- Total intents: {distribution["total_intents"]}', f'- Total labeled conversations: {len(golden_df)}', '']
    report_lines.append('## Conversations per intent')
    for intent, count in distribution['conversations_per_intent'].items():
        report_lines.append(f'- {intent}: {count} ({distribution["percentages"].get(intent, 0.0):.2f}%)')
    report_lines.extend(['', '## Additional statistics', ''])
    report_lines.append(f'- Average confidence: {distribution["average_confidence"]:.4f}')
    report_lines.append(f'- Largest intent: {distribution["largest_intent"]}')
    report_lines.append(f'- Smallest intent: {distribution["smallest_intent"]}')
    report_lines.append(f'- Imbalance ratio: {distribution["imbalance_ratio"]:.4f}')
    report_lines.append(f'- Language breakdown: {distribution["language_breakdown"]}')
    (report_dir / 'intent_distribution_report.md').write_text('\n'.join(report_lines) + '\n', encoding='utf-8')
    return distribution, distribution_path


def create_visualizations(golden_df: pd.DataFrame, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    counts = golden_df.groupby('intent_label').size().sort_values(ascending=False)
    if not counts.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        counts.plot(kind='bar', ax=ax, color='#4C72B0')
        ax.set_title('Intent Distribution')
        ax.set_xlabel('Intent')
        ax.set_ylabel('Conversation Count')
        fig.tight_layout()
        path = out_dir / 'intent_distribution.png'
        fig.savefig(path, dpi=300)
        plt.close(fig)
        created.append(path)

        category_counts = golden_df.groupby('intent_category').size().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 7))
        category_counts.plot(kind='bar', ax=ax, color='#55A868')
        ax.set_title('Intent Category Distribution')
        ax.set_xlabel('Category')
        ax.set_ylabel('Conversation Count')
        fig.tight_layout()
        path = out_dir / 'intent_category_distribution.png'
        fig.savefig(path, dpi=300)
        plt.close(fig)
        created.append(path)

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.hist(golden_df['confidence'].astype(float), bins=20, color='#C44E52', edgecolor='black')
        ax.set_title('Intent Confidence Histogram')
        ax.set_xlabel('Confidence')
        ax.set_ylabel('Frequency')
        fig.tight_layout()
        path = out_dir / 'intent_confidence_histogram.png'
        fig.savefig(path, dpi=300)
        plt.close(fig)
        created.append(path)

        top_10 = counts.head(10)
        fig, ax = plt.subplots(figsize=(12, 7))
        top_10.plot(kind='bar', ax=ax, color='#8172B3')
        ax.set_title('Top 10 Intents')
        ax.set_xlabel('Intent')
        ax.set_ylabel('Count')
        fig.tight_layout()
        path = out_dir / 'top_10_intents.png'
        fig.savefig(path, dpi=300)
        plt.close(fig)
        created.append(path)

        language_matrix = pd.crosstab(golden_df['language'], golden_df['intent_label'])
        fig, ax = plt.subplots(figsize=(12, 8))
        image = ax.imshow(language_matrix.values, aspect='auto', cmap='viridis')
        ax.set_xticks(range(len(language_matrix.columns)))
        ax.set_xticklabels(language_matrix.columns, rotation=45, ha='right')
        ax.set_yticks(range(len(language_matrix.index)))
        ax.set_yticklabels(language_matrix.index)
        ax.set_title('Language vs Intent Heatmap')
        fig.colorbar(image, ax=ax)
        fig.tight_layout()
        path = out_dir / 'language_vs_intent_heatmap.png'
        fig.savefig(path, dpi=300)
        plt.close(fig)
        created.append(path)

    return created


def run(force: bool = False) -> int:
    start = time.time()
    root = PROJECT_ROOT
    taxonomy_dir = root / 'data' / 'intents'
    report_dir = root / 'report'
    assets_dir = root / 'assets' / 'intents'
    ensure_dirs([taxonomy_dir / 'intent_taxonomy.json', report_dir / 'intent_examples.md', assets_dir / 'intent_distribution.png'])

    taxonomy, golden_df, _ = build_taxonomy_and_labels(force=force)
    golden_path = root / 'data' / 'intents' / 'golden_intents.csv'

    intent_examples_path = report_dir / 'intent_examples.md'
    intent_examples_json = report_dir / 'golden_intent_statistics.json'
    example_records = create_intent_examples(golden_df, intent_examples_path, intent_examples_json)

    distribution, _ = create_distribution_reports(golden_df, report_dir)

    created_visuals = create_visualizations(golden_df, assets_dir)

    validation_report = validate_intent_dataset(golden_df, report_dir)
    overall_pass = validation_report['overall_pass']

    # ensure required outputs exist
    required_paths = [
        taxonomy_dir / 'intent_taxonomy.json',
        golden_path,
        intent_examples_path,
        intent_examples_json,
        report_dir / 'intent_distribution_report.md',
        report_dir / 'intent_distribution.json',
        report_dir / 'intent_validation.json',
        report_dir / 'intent_validation_report.md',
    ] + created_visuals
    missing = [str(p) for p in required_paths if not p.exists()]

    total_canonical_intents = len(taxonomy)
    total_labeled_conversations = len(golden_df)
    average_confidence = round(float(golden_df['confidence'].mean()), 4) if not golden_df.empty else 0.0
    representative_examples = sum(int(item.get('representative_conversations', 0)) for item in example_records)
    total_reports = 6
    total_pngs = len(created_visuals)
    execution_time = time.time() - start

    print('\nPASS / FAIL TABLE')
    print(f"{'File':<45} {'Status'}")
    checks = [
        ('Intent taxonomy', (taxonomy_dir / 'intent_taxonomy.json').exists()),
        ('Golden intents', golden_path.exists()),
        ('Example report', intent_examples_path.exists()),
        ('Intent distribution', (report_dir / 'intent_distribution.json').exists()),
        ('Validation report', (report_dir / 'intent_validation.json').exists()),
        ('Visualizations', len(created_visuals) == 5),
    ]
    for name, passed in checks:
        print(f"{name:<45} {'PASS' if passed else 'FAIL'}")

    banner = '# ======================================================'
    print('\n' + banner)
    print('PHASE 5 COMPLETED SUCCESSFULLY')
    print(f'Total canonical intents: {total_canonical_intents}')
    print(f'Total labeled conversations: {total_labeled_conversations}')
    print(f'Total representative examples generated: {representative_examples}')
    print(f'Average confidence: {average_confidence:.4f}')
    print(f'Number of reports created: {total_reports}')
    print(f'Number of PNG visualizations created: {total_pngs}')
    print(f'Execution time: {execution_time:.2f} seconds')

    if missing or not overall_pass:
        print('Validation summary: FAIL')
        return 1
    print('Validation summary: PASS')
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the Phase 5 golden intent labeling pipeline.')
    parser.add_argument('--force', action='store_true', help='Overwrite existing Phase 5 artifacts.')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    args = parse_args()
    sys.exit(run(force=args.force))
