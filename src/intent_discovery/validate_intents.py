from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def infer_language(text: str) -> str:
    if text is None:
        return 'unknown'
    value = str(text).lower()
    if any(token in value for token in ['bonjour', 'merci', "s'il", 'le colis', 'je', 'vous', 'la commande', 'livraison']):
        return 'fr'
    if any(token in value for token in ['hallo', 'ich', 'die', 'und', 'nicht', 'bitte', 'danke', 'bestellung']):
        return 'de'
    if any(token in value for token in ['hola', 'gracias', 'pedido', 'envío', 'por favor', 'cliente', 'artículo']):
        return 'es'
    if any(token in value for token in ['olá', 'obrigado', 'pedido', 'envio', 'produto', 'livro', 'entrega']):
        return 'pt'
    if any(token in value for token in ['こんにちは', 'ありがとうございます', '配送', '注文', '商品', 'amazon']):
        return 'ja'
    if any(token in value for token in ['привет', 'спасибо', 'заказ', 'доставка', 'товар']):
        return 'ru'
    if any(token in value for token in ['hello', 'order', 'delivery', 'refund', 'prime', 'amazon', 'customer']):
        return 'en'
    return 'unknown'


def canonical_intent_taxonomy() -> list[dict[str, Any]]:
    taxonomy = [
        {
            'intent_id': 'INT-001',
            'intent_label': 'Orders & Tracking',
            'intent_category': 'Orders',
            'cluster_ids': [1],
            'keywords': ['order', 'delivery', 'tracking', 'shipment', 'package', 'cancel', 'status'],
            'description': 'Customer requests about placing, modifying, or tracking orders.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        {
            'intent_id': 'INT-002',
            'intent_label': 'Delivery Issue',
            'intent_category': 'Delivery',
            'cluster_ids': [2, 3],
            'keywords': ['delivery', 'late', 'shipment', 'carrier', 'missing', 'amazon logistics', 'tracking'],
            'description': 'Problems involving late, missing, or carrier-delivery communication.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        {
            'intent_id': 'INT-003',
            'intent_label': 'Returns & Refunds',
            'intent_category': 'Returns & Refunds',
            'cluster_ids': [8],
            'keywords': ['return', 'refund', 'replacement', 'exchange', 'money back', 'cancel order'],
            'description': 'Return, refund, replacement, and reimbursement related support requests.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        {
            'intent_id': 'INT-004',
            'intent_label': 'Prime Membership',
            'intent_category': 'Prime Membership',
            'cluster_ids': [4, 5],
            'keywords': ['prime', 'membership', 'student', 'free trial', 'benefits', 'subscription', 'billing'],
            'description': 'Question and support needs for Prime subscriptions, billing, and membership benefits.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        {
            'intent_id': 'INT-005',
            'intent_label': 'Login & Authentication',
            'intent_category': 'Login & Authentication',
            'cluster_ids': [6, 7],
            'keywords': ['login', 'password', 'account', 'authenticate', 'verification', 'reset', 'signin'],
            'description': 'Authentication, login, password, and account access issues.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        {
            'intent_id': 'INT-006',
            'intent_label': 'Promotions & Coupons',
            'intent_category': 'Promotions & Coupons',
            'cluster_ids': [0],
            'keywords': ['contest', 'promotion', 'coupon', 'winner', 'quiz', 'giveaway', 'results'],
            'description': 'Contest, giveaway, and promotional activity questions or complaints.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        {
            'intent_id': 'INT-007',
            'intent_label': 'Technical Issue',
            'intent_category': 'Technical Issue',
            'cluster_ids': [9],
            'keywords': ['device', 'kindle', 'fire tv', 'technical', 'error', 'app', 'problem', 'bug'],
            'description': 'Product or platform technical problems and troubleshooting requests.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        {
            'intent_id': 'INT-008',
            'intent_label': 'Other',
            'intent_category': 'Other',
            'cluster_ids': [],
            'keywords': ['other', 'uncategorized', 'miscellaneous'],
            'description': 'Miscellaneous or unclassified support needs.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
    ]
    return taxonomy


def build_taxonomy_from_cluster_summary(summary_df: pd.DataFrame, taxonomy_path: Path) -> list[dict[str, Any]]:
    summary_df = summary_df.copy()
    cluster_map = {
        0: ('INT-006', 'Promotions & Coupons'),
        1: ('INT-001', 'Orders'),
        2: ('INT-002', 'Delivery'),
        3: ('INT-002', 'Delivery'),
        4: ('INT-004', 'Prime Membership'),
        5: ('INT-004', 'Prime Membership'),
        6: ('INT-005', 'Login & Authentication'),
        7: ('INT-005', 'Login & Authentication'),
        8: ('INT-003', 'Returns & Refunds'),
        9: ('INT-007', 'Technical Issue'),
    }

    taxonomy = canonical_intent_taxonomy()
    tax_map = {entry['intent_id']: entry for entry in taxonomy}
    for cluster_id, (intent_id, category) in cluster_map.items():
        entry = tax_map.setdefault(intent_id, {
            'intent_id': intent_id,
            'intent_label': category,
            'intent_category': category,
            'cluster_ids': [],
            'keywords': [],
            'description': 'Automatically mapped cluster category.',
            'conversation_count': 0,
            'created_at': datetime.now(timezone.utc).isoformat(),
        })
        if cluster_id not in entry['cluster_ids']:
            entry['cluster_ids'] = sorted(entry['cluster_ids'] + [cluster_id])
        row = summary_df[summary_df['cluster_id'] == cluster_id]
        if not row.empty:
            top_keywords = str(row.iloc[0].get('top_keywords', ''))
            keywords = [kw.strip() for kw in top_keywords.split(',') if kw.strip()]
            entry['keywords'] = keywords[:12]
            entry['conversation_count'] = int(row.iloc[0].get('conversation_count', 0))
            entry['intent_label'] = str(row.iloc[0].get('intent_label', entry['intent_label']))
            entry['intent_category'] = category

    other = tax_map['INT-008']
    if not other['cluster_ids']:
        other['cluster_ids'] = []

    output = []
    for entry in taxonomy:
        if entry['intent_id'] in tax_map:
            selected = tax_map[entry['intent_id']]
            output.append({
                'intent_id': selected['intent_id'],
                'intent_label': selected['intent_label'],
                'intent_category': selected['intent_category'],
                'cluster_ids': sorted(selected.get('cluster_ids', [])),
                'keywords': selected.get('keywords', []),
                'description': selected.get('description', ''),
                'conversation_count': int(selected.get('conversation_count', 0)),
                'created_at': selected.get('created_at', datetime.now(timezone.utc).isoformat()),
            })
    taxonomy_path.parent.mkdir(parents=True, exist_ok=True)
    taxonomy_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    return output


def build_golden_intents(
    labels_df: pd.DataFrame,
    sample_df: pd.DataFrame,
    taxonomy: list[dict[str, Any]],
    random_state: int = 42,
) -> pd.DataFrame:
    labels_df = labels_df.copy()
    sample_df = sample_df.copy()

    if 'conversation_id' not in labels_df.columns or 'conversation_id' not in sample_df.columns:
        raise ValueError('Both Phase 4 label data and sample data must contain conversation_id.')

    labels_df = labels_df.rename(columns={
        'cluster_id': 'cluster_id',
        'probability': 'confidence',
    })

    merged = labels_df.merge(sample_df[['conversation_id', 'clean_text', 'message_count', 'customer_message_count', 'amazon_message_count']], on='conversation_id', how='left')
    merged = merged.sort_values('conversation_id').reset_index(drop=True)

    cluster_lookup = {}
    for item in taxonomy:
        for cluster_id in item.get('cluster_ids', []):
            cluster_lookup[int(cluster_id)] = {
                'intent_label': item['intent_label'],
                'intent_category': item['intent_category'],
            }

    def map_intent(cluster_id: Any) -> tuple[str, str]:
        cluster_id = int(cluster_id)
        if cluster_id in cluster_lookup:
            return cluster_lookup[cluster_id]['intent_label'], cluster_lookup[cluster_id]['intent_category']
        return 'Other', 'Other'

    merged['intent_label'], merged['intent_category'] = zip(*merged['cluster_id'].map(map_intent))
    merged['confidence'] = merged['confidence'].fillna(0.0).clip(0.0, 1.0)
    merged['language'] = merged['clean_text'].map(infer_language)
    merged['cluster_id'] = pd.to_numeric(merged['cluster_id'], errors='coerce').fillna(-1).astype(int)
    merged['intent_label'] = merged['intent_label'].fillna('Other')
    merged['intent_category'] = merged['intent_category'].fillna('Other')
    merged['clean_text'] = merged['clean_text'].fillna('').astype(str)

    golden = merged[[
        'conversation_id',
        'cluster_id',
        'clean_text',
        'intent_label',
        'intent_category',
        'confidence',
        'language',
        'message_count',
        'customer_message_count',
        'amazon_message_count',
    ]].copy()

    golden = golden.drop_duplicates(subset='conversation_id', keep='first').reset_index(drop=True)
    golden['conversation_id'] = golden['conversation_id'].astype(str)
    golden['intent_label'] = golden['intent_label'].replace('', 'Other')
    golden['intent_category'] = golden['intent_category'].replace('', 'Other')
    golden['confidence'] = golden['confidence'].astype(float)
    return golden


def _validation_checks(golden: pd.DataFrame) -> tuple[dict[str, bool], list[str]]:
    issues: list[str] = []
    checks: dict[str, bool] = {
        'missing_labels': True,
        'duplicate_conversation_ids': True,
        'valid_confidence': True,
        'missing_clean_text': True,
        'missing_categories': True,
        'cluster_coverage': True,
        'intent_coverage': True,
        'empty_intents': True,
        'unicode_integrity': True,
    }

    if golden['intent_label'].isna().any():
        checks['missing_labels'] = False
        issues.append('Missing intent labels detected.')
    if golden['conversation_id'].duplicated().any():
        checks['duplicate_conversation_ids'] = False
        issues.append('Duplicate conversation IDs detected.')
    if not golden['confidence'].between(0, 1).all():
        checks['valid_confidence'] = False
        issues.append('Confidence values outside 0-1 range detected.')
    if golden['clean_text'].isna().any() or (golden['clean_text'].astype(str).str.strip() == '').any():
        checks['missing_clean_text'] = False
        issues.append('Missing or empty clean_text values detected.')
    if golden['intent_category'].isna().any() or (golden['intent_category'].astype(str).str.strip() == '').any():
        checks['missing_categories'] = False
        issues.append('Missing or empty categories detected.')
    if golden['cluster_id'].isna().any():
        checks['cluster_coverage'] = False
        issues.append('Some cluster IDs are missing.')
    if golden['intent_label'].nunique() == 0:
        checks['intent_coverage'] = False
        issues.append('No intent labels available.')
    if golden.groupby('intent_label').size().le(0).any():
        checks['empty_intents'] = False
        issues.append('At least one intent is empty.')
    try:
        for text in golden['clean_text'].astype(str):
            text.encode('utf-8')
    except Exception:
        checks['unicode_integrity'] = False
        issues.append('UTF-8 encoding failed for at least one text field.')

    return checks, issues


def validate_intent_dataset(golden_df: pd.DataFrame, output_dir: Path) -> dict[str, Any]:
    checks, issues = _validation_checks(golden_df)
    summary = {
        'total_rows': int(len(golden_df)),
        'total_unique_conversations': int(golden_df['conversation_id'].nunique()),
        'total_intents': int(golden_df['intent_label'].nunique()),
        'total_categories': int(golden_df['intent_category'].nunique()),
        'average_confidence': round(float(golden_df['confidence'].mean()), 4) if not golden_df.empty else 0.0,
        'missing_labels': int(golden_df['intent_label'].isna().sum()),
        'duplicate_conversation_ids': int(golden_df['conversation_id'].duplicated().sum()),
        'empty_intents': int((golden_df.groupby('intent_label').size() == 0).sum()),
    }
    overall_pass = all(checks.values())

    report = {
        'overall_pass': overall_pass,
        'checks': checks,
        'issues': issues,
        'summary': summary,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / 'intent_validation.json'
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    md_lines = ['# Intent Validation Report', '', '## Summary', '']
    for key, value in summary.items():
        md_lines.append(f'- {key}: {value}')
    md_lines.extend(['', '## Checks', ''])
    for check_name, passed in checks.items():
        md_lines.append(f'- {check_name}: {"PASS" if passed else "FAIL"}')
    md_lines.extend(['', '## Issues', ''])
    if issues:
        md_lines.extend(f'- {issue}' for issue in issues)
    else:
        md_lines.append('No issues detected.')
    md_lines.append('')
    (output_dir / 'intent_validation_report.md').write_text('\n'.join(md_lines) + '\n', encoding='utf-8')
    return report


def build_distribution_summary(golden_df: pd.DataFrame) -> dict[str, Any]:
    golden_df = golden_df.copy()
    if golden_df.empty:
        return {
            'total_intents': 0,
            'conversations_per_intent': {},
            'percentages': {},
            'average_confidence': 0.0,
            'language_breakdown': {},
            'largest_intent': None,
            'smallest_intent': None,
            'imbalance_ratio': 0.0,
        }

    counts = golden_df.groupby('intent_label').size().sort_values(ascending=False)
    total = int(counts.sum())
    language_breakdown = golden_df['language'].value_counts().to_dict()
    average_confidence = round(float(golden_df['confidence'].mean()), 4)

    distribution = {
        'total_intents': int(counts.shape[0]),
        'conversations_per_intent': {str(label): int(value) for label, value in counts.items()},
        'percentages': {str(label): round(float(value / total * 100.0), 4) for label, value in counts.items()},
        'average_confidence': average_confidence,
        'language_breakdown': {str(k): int(v) for k, v in language_breakdown.items()},
        'largest_intent': str(counts.idxmax()) if not counts.empty else None,
        'smallest_intent': str(counts.idxmin()) if not counts.empty else None,
        'imbalance_ratio': round(float(counts.max() / counts.min()) if counts.min() > 0 else 0.0, 4),
    }
    return distribution
