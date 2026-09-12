from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INTENT_TAXONOMY = ROOT / 'data' / 'intents' / 'intent_taxonomy.json'
GOLDEN_INTENTS = ROOT / 'data' / 'intents' / 'golden_intents.csv'
INTENT_EXAMPLES = ROOT / 'report' / 'intent_examples.md'
INTENT_VALIDATION = ROOT / 'report' / 'intent_validation.json'
KNOWLEDGE_DOCS = ROOT / 'data' / 'knowledge_base' / 'knowledge_documents.parquet'
KNOWLEDGE_CSV = ROOT / 'data' / 'knowledge_base' / 'knowledge_documents.csv'
KNOWLEDGE_EMB = ROOT / 'data' / 'knowledge_base' / 'knowledge_embeddings.npy'
DOC_META = ROOT / 'data' / 'knowledge_base' / 'document_metadata.csv'
FAISS_INDEX = ROOT / 'models' / 'faiss' / 'amazon_support.index'
FAISS_META = ROOT / 'models' / 'faiss' / 'index_metadata.json'
EVAL_QUERIES = ROOT / 'data' / 'evaluation' / 'retrieval_eval_queries.csv'
METRICS = ROOT / 'report' / 'retrieval_metrics.json'
METRICS_MD = ROOT / 'report' / 'retrieval_evaluation.md'

VISUALS = [
    ROOT / 'assets' / 'retrieval' / 'intent_distribution.png',
    ROOT / 'assets' / 'retrieval' / 'knowledge_base_size.png',
    ROOT / 'assets' / 'retrieval' / 'confidence_histogram.png',
    ROOT / 'assets' / 'retrieval' / 'embedding_similarity_histogram.png',
    ROOT / 'assets' / 'retrieval' / 'recall_at_k.png',
]


def test_phase56_artifacts_exist() -> None:
    for path in [
        INTENT_TAXONOMY,
        GOLDEN_INTENTS,
        INTENT_EXAMPLES,
        INTENT_VALIDATION,
        KNOWLEDGE_DOCS,
        KNOWLEDGE_CSV,
        KNOWLEDGE_EMB,
        DOC_META,
        FAISS_INDEX,
        FAISS_META,
        EVAL_QUERIES,
        METRICS,
        METRICS_MD,
    ]:
        assert path.exists(), f'Missing required artifact: {path}'

    taxonomy = json.loads(INTENT_TAXONOMY.read_text(encoding='utf-8'))
    assert 'Customer Support' in taxonomy

    golden = pd.read_csv(GOLDEN_INTENTS)
    assert {'conversation_id', 'cluster_id', 'intent_label', 'intent_category', 'confidence'}.issubset(golden.columns)
    assert len(golden) > 0

    eval_queries = pd.read_csv(EVAL_QUERIES)
    assert {'query', 'expected_intent', 'conversation_id', 'language'}.issubset(eval_queries.columns)
    assert len(eval_queries) >= 200


def test_retrieval_metrics_and_visuals() -> None:
    metrics = json.loads(METRICS.read_text(encoding='utf-8'))
    for key in ['recall_at_1', 'recall_at_3', 'recall_at_5', 'mrr', 'hit_rate', 'average_similarity_score']:
        assert key in metrics, key

    for p in VISUALS:
        assert p.exists(), f'Missing visualization: {p}'
