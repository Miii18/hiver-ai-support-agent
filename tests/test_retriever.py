from __future__ import annotations

import numpy as np

from src.retrieval.retriever import load_index, encode_query, retrieve


def test_retriever_basic_api() -> None:
    index = load_index()
    assert index is not None

    query_vec = encode_query('Where is my order?')
    assert query_vec.shape[0] > 0

    results = retrieve('Where is my order?', top_k=5)
    assert len(results) == 5
    assert {'conversation_id', 'intent', 'score', 'customer_query', 'amazon_response'}.issubset(results[0].keys())


def test_retriever_scores_are_numeric() -> None:
    results = retrieve('delivery problem', top_k=3)
    scores = [float(item['score']) for item in results]
    assert all(np.isfinite(scores))
    assert scores[0] >= scores[-1]
