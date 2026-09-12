from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.retrieval.retriever import retrieve

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _pass_fail_table(results: dict[str, bool]) -> None:
    print('PASS / FAIL TABLE')
    print(f"{'Check':<40} {'Status':<6}")
    for name, ok in results.items():
        print(f"{name:<40} {'PASS' if ok else 'FAIL':<6}")
    if not all(results.values()):
        raise AssertionError('One or more Phase 6 validation checks failed.')


def test_phase6_outputs() -> None:
    required = {
        'Knowledge documents exist': (PROJECT_ROOT / 'data' / 'knowledge_base' / 'knowledge_documents.parquet').exists(),
        'Embeddings exist': (PROJECT_ROOT / 'data' / 'knowledge_base' / 'knowledge_embeddings.npy').exists(),
        'Metadata exists': (PROJECT_ROOT / 'data' / 'knowledge_base' / 'document_metadata.csv').exists(),
        'FAISS index exists': (PROJECT_ROOT / 'models' / 'faiss' / 'amazon_support.index').exists(),
        'Evaluation CSV exists': (PROJECT_ROOT / 'data' / 'evaluation' / 'retrieval_eval_queries.csv').exists(),
        'Metrics JSON exists': (PROJECT_ROOT / 'report' / 'retrieval_metrics.json').exists(),
        'Markdown report exists': (PROJECT_ROOT / 'report' / 'retrieval_evaluation.md').exists(),
        'knowledge_base_size.png exists': (PROJECT_ROOT / 'assets' / 'retrieval' / 'knowledge_base_size.png').exists(),
        'intent_distribution.png exists': (PROJECT_ROOT / 'assets' / 'retrieval' / 'intent_distribution.png').exists(),
        'embedding_similarity_histogram.png exists': (PROJECT_ROOT / 'assets' / 'retrieval' / 'embedding_similarity_histogram.png').exists(),
        'recall_at_k.png exists': (PROJECT_ROOT / 'assets' / 'retrieval' / 'recall_at_k.png').exists(),
        'language_recall.png exists': (PROJECT_ROOT / 'assets' / 'retrieval' / 'language_recall.png').exists(),
    }

    results = retrieve('where is my order?', top_k=5)
    required['Retriever returns top-5 results'] = isinstance(results, pd.DataFrame) and len(results) > 0

    _pass_fail_table(required)

    assert (PROJECT_ROOT / 'data' / 'knowledge_base' / 'knowledge_documents.parquet').exists()
    assert (PROJECT_ROOT / 'data' / 'knowledge_base' / 'knowledge_embeddings.npy').exists()
    assert (PROJECT_ROOT / 'models' / 'faiss' / 'amazon_support.index').exists()
    assert (PROJECT_ROOT / 'data' / 'evaluation' / 'retrieval_eval_queries.csv').exists()
    assert (PROJECT_ROOT / 'report' / 'retrieval_metrics.json').exists()
    assert (PROJECT_ROOT / 'report' / 'retrieval_evaluation.md').exists()
    assert len(results) > 0


def test_phase6_success_banner_exact(capsys, monkeypatch) -> None:
    root = PROJECT_ROOT
    spec = importlib.util.spec_from_file_location('phase6_runner', root / 'scripts' / 'run_phase6.py')
    runner = importlib.util.module_from_spec(spec)
    assert spec and spec.loader is not None
    spec.loader.exec_module(runner)

    monkeypatch.setattr(runner, 'build_knowledge_documents', lambda force=False: pd.DataFrame([{'conversation_id': 'c1'}]))
    monkeypatch.setattr(runner, 'generate_document_embeddings', lambda force=False: (np.ones((1, 3), dtype=np.float32), pd.DataFrame({'document_id': ['d1']})))
    monkeypatch.setattr(runner, 'build_faiss_index', lambda force=False: (root / 'models' / 'faiss' / 'amazon_support.index', {'document_count': 1}))
    monkeypatch.setattr(runner, 'generate_retrieval_eval_queries', lambda docs, n_queries=250: pd.DataFrame([{'query': 'where is my order?', 'conversation_id': 'c1'}]))
    monkeypatch.setattr(runner, 'evaluate_retrieval', lambda results, queries: {'Recall@1': 1.0, 'Recall@3': 1.0, 'Recall@5': 1.0, 'MRR': 1.0, 'Hit Rate': 1.0})
    monkeypatch.setattr(runner, 'create_visualizations', lambda out_dir: [])
    monkeypatch.setattr(runner, 'validate_outputs', lambda: ({}, 0))

    exit_code = runner.run(force=False)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert '# ====================================================== PHASE 6 COMPLETED SUCCESSFULLY' in captured.out


if __name__ == '__main__':
    test_phase6_outputs()
