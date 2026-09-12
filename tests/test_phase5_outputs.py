from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

TAXONOMY = ROOT / 'data' / 'intents' / 'intent_taxonomy.json'
GOLDEN = ROOT / 'data' / 'intents' / 'golden_intents.csv'
INTENT_EXAMPLES = ROOT / 'report' / 'intent_examples.md'
INTENT_STATS = ROOT / 'report' / 'golden_intent_statistics.json'
INTENT_DIST_REPORT = ROOT / 'report' / 'intent_distribution_report.md'
INTENT_DIST_JSON = ROOT / 'report' / 'intent_distribution.json'
VALIDATION_JSON = ROOT / 'report' / 'intent_validation.json'
VALIDATION_MD = ROOT / 'report' / 'intent_validation_report.md'

VISUALS = [
    ROOT / 'assets' / 'intents' / 'intent_distribution.png',
    ROOT / 'assets' / 'intents' / 'intent_category_distribution.png',
    ROOT / 'assets' / 'intents' / 'intent_confidence_histogram.png',
    ROOT / 'assets' / 'intents' / 'top_10_intents.png',
    ROOT / 'assets' / 'intents' / 'language_vs_intent_heatmap.png',
]


def test_phase5_outputs_exist() -> None:
    required = [
        TAXONOMY,
        GOLDEN,
        INTENT_EXAMPLES,
        INTENT_STATS,
        INTENT_DIST_REPORT,
        INTENT_DIST_JSON,
        VALIDATION_JSON,
        VALIDATION_MD,
    ]
    for path in required:
        assert path.exists(), f'Missing required file: {path}'

    taxonomy = json.loads(TAXONOMY.read_text(encoding='utf-8'))
    assert isinstance(taxonomy, list)
    assert len(taxonomy) > 0

    golden = pd.read_csv(GOLDEN)
    assert {'conversation_id', 'cluster_id', 'clean_text', 'intent_label', 'intent_category', 'confidence'}.issubset(golden.columns)
    assert golden['conversation_id'].is_unique
    assert golden['intent_label'].notna().all()
    assert (golden['confidence'].between(0, 1)).all()


def test_phase5_visualization_outputs_exist() -> None:
    for path in VISUALS:
        assert path.exists(), f'Missing visualization: {path}'


def test_phase5_validation_json_is_valid() -> None:
    validation = json.loads(VALIDATION_JSON.read_text(encoding='utf-8'))
    assert 'overall_pass' in validation
    assert 'issues' in validation
    assert 'summary' in validation
