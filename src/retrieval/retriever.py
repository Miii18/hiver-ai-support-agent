from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np
import pandas as pd

HF_CACHE = Path(r'D:\AI\hf_cache')
HF_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('HF_HOME', str(HF_CACHE))
os.environ.setdefault('TRANSFORMERS_CACHE', str(HF_CACHE / 'transformers'))
os.environ.setdefault('HUGGINGFACE_HUB_CACHE', str(HF_CACHE / 'hub'))

from sentence_transformers import SentenceTransformer

LOGGER = logging.getLogger('retriever')
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_ROOT / 'models' / 'faiss' / 'amazon_support.index'
INDEX_META_PATH = PROJECT_ROOT / 'models' / 'faiss' / 'index_metadata.json'
DOC_METADATA_PATH = PROJECT_ROOT / 'data' / 'knowledge_base' / 'document_metadata.csv'
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
_MODEL_CACHE: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = SentenceTransformer(MODEL_NAME, device='cpu')
    return _MODEL_CACHE


def load_index() -> dict[str, Any]:
    """Load the FAISS index and supporting metadata for retrieval."""
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f'FAISS index not found: {INDEX_PATH}')
    if not DOC_METADATA_PATH.exists():
        raise FileNotFoundError(f'Document metadata not found: {DOC_METADATA_PATH}')

    index = faiss.read_index(str(INDEX_PATH))
    metadata = pd.read_csv(DOC_METADATA_PATH, encoding='utf-8', on_bad_lines='skip')
    with INDEX_META_PATH.open('r', encoding='utf-8') as fh:
        index_meta = json.load(fh)
    model = _get_model()

    LOGGER.info('Loaded FAISS index with %d documents and dimension %s', len(metadata), index.d)
    return {
        'index': index,
        'documents': metadata,
        'model': model,
        'metadata': index_meta,
    }


def encode_query(query: str) -> np.ndarray:
    """Encode a single query using the same MiniLM model as the knowledge base."""
    model = _get_model()
    vector = model.encode([str(query).strip()], convert_to_numpy=True, normalize_embeddings=True)
    return np.asarray(vector, dtype=np.float32).reshape(1, -1)


def retrieve(query: str, top_k: int = 5) -> pd.DataFrame:
    """Retrieve the most similar conversations for a query using cosine similarity."""
    if top_k <= 0:
        raise ValueError('top_k must be positive')

    index_data = load_index()
    index = index_data['index']
    documents = index_data['documents']
    model = index_data['model']

    vector = model.encode([str(query).strip()], convert_to_numpy=True, normalize_embeddings=True)
    vector = np.asarray(vector, dtype=np.float32).reshape(1, -1)
    scores, neighbor_ids = index.search(vector, min(top_k, len(documents)))

    rows: list[dict[str, Any]] = []
    for score, doc_idx in zip(scores[0], neighbor_ids[0]):
        if doc_idx < 0:
            continue
        doc = documents.iloc[int(doc_idx)].copy()
        rows.append({
            'conversation_id': doc.get('conversation_id', ''),
            'intent_label': doc.get('intent_label', ''),
            'intent_category': doc.get('intent_category', ''),
            'customer_query': doc.get('customer_query', ''),
            'amazon_response': doc.get('amazon_response', ''),
            'similarity_score': float(score),
            'document_id': doc.get('document_id', ''),
        })

    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(columns=[
            'conversation_id',
            'intent_label',
            'intent_category',
            'customer_query',
            'amazon_response',
            'similarity_score',
            'document_id',
        ])

    result = result.sort_values('similarity_score', ascending=False, kind='mergesort').reset_index(drop=True)
    return result
