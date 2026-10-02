from __future__ import annotations

import numpy as np
import pandas as pd

from src.retrieval.retriever import load_index, encode_query, retrieve


def test_retriever_basic_api() -> None:
    index_data = load_index()
    assert index_data is not None

    query_vec = encode_query('Where is my order?')
    assert query_vec.shape[0] > 0

    results = retrieve('Where is my order?', top_k=5)
    assert len(results) == 5
    if isinstance(results, pd.DataFrame):
        assert {'conversation_id', 'intent_label', 'similarity_score', 'customer_query', 'amazon_response'}.issubset(results.columns)
    else:
        assert {'conversation_id', 'customer_query', 'amazon_response'}.issubset(results[0].keys())


def test_retriever_scores_are_numeric() -> None:
    results = retrieve('delivery problem', top_k=3)
    if isinstance(results, pd.DataFrame):
        scores = [float(s) for s in results['similarity_score']]
    else:
        scores = [float(item.get('similarity_score', item.get('score', 0))) for item in results]
    assert all(np.isfinite(scores))
    assert scores[0] >= scores[-1]
