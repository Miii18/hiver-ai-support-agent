from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

HF_CACHE = Path(r'D:\AI\hf_cache')
HF_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('HF_HOME', str(HF_CACHE))
os.environ.setdefault('TRANSFORMERS_CACHE', str(HF_CACHE / 'transformers'))
os.environ.setdefault('HUGGINGFACE_HUB_CACHE', str(HF_CACHE / 'hub'))

from sentence_transformers import SentenceTransformer

LOGGER = logging.getLogger('knowledge_base')
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = PROJECT_ROOT / 'data' / 'knowledge_base'
DOCUMENTS_PARQUET = KNOWLEDGE_DIR / 'knowledge_documents.parquet'
DOCUMENTS_CSV = KNOWLEDGE_DIR / 'knowledge_documents.csv'
EMBEDDINGS_PATH = KNOWLEDGE_DIR / 'knowledge_embeddings.npy'
DOCUMENT_METADATA_PATH = KNOWLEDGE_DIR / 'document_metadata.csv'


def _split_customer_and_amazon(text: str) -> tuple[str, str]:
    content = str(text or '')
    if 'Amazon:' in content:
        customer_part, amazon_part = content.split('Amazon:', 1)
        customer = customer_part.replace('Customer:', '', 1).strip()
        amazon = amazon_part.strip()
        return customer, amazon
    return content.strip(), ''


def load_documents() -> pd.DataFrame:
    """Load the Phase 6 knowledge document catalog as a dataframe."""
    path = DOCUMENTS_PARQUET if DOCUMENTS_PARQUET.exists() else DOCUMENTS_CSV
    if not path.exists():
        raise FileNotFoundError(f'Knowledge documents not found at {path}')
    if path.suffix == '.parquet':
        return pd.read_parquet(path)
    return pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')


def load_embeddings() -> np.ndarray:
    """Load the knowledge-base embedding matrix."""
    if not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(f'Embeddings not found at {EMBEDDINGS_PATH}')
    return np.load(EMBEDDINGS_PATH)


def search_by_intent(intent_label: str) -> pd.DataFrame:
    """Return all knowledge documents assigned to the requested intent label."""
    docs = load_documents()
    return docs[docs['intent_label'].astype(str) == str(intent_label)].reset_index(drop=True)


def search_by_language(language: str) -> pd.DataFrame:
    """Return all knowledge documents in the requested language code."""
    docs = load_documents()
    return docs[docs['language'].astype(str) == str(language)].reset_index(drop=True)


def get_document(document_id: str) -> dict[str, Any] | None:
    """Retrieve a single document by deterministic document ID."""
    docs = load_documents()
    match = docs[docs['document_id'].astype(str) == str(document_id)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def summarize_document(document_id: str) -> dict[str, Any]:
    """Summarize a knowledge document for debugging and reporting."""
    doc = get_document(document_id)
    if doc is None:
        raise ValueError(f'Document not found: {document_id}')
    customer_query, amazon_response = _split_customer_and_amazon(doc.get('conversation', ''))
    summary = {
        'document_id': doc.get('document_id'),
        'conversation_id': doc.get('conversation_id'),
        'intent_label': doc.get('intent_label'),
        'intent_category': doc.get('intent_category'),
        'language': doc.get('language'),
        'message_count': doc.get('message_count'),
        'customer_query_preview': customer_query[:200],
        'amazon_response_preview': amazon_response[:200],
    }
    return summary


def build_knowledge_documents(force: bool = False) -> pd.DataFrame:
    """Construct the Phase 6 knowledge-base documents from the Phase 5 outputs."""
    golden_path = PROJECT_ROOT / 'data' / 'intents' / 'golden_intents.csv'
    sample_path = PROJECT_ROOT / 'data' / 'processed' / 'amazon_conversations_sample.csv'
    out_csv = DOCUMENTS_CSV
    out_parquet = DOCUMENTS_PARQUET

    if out_csv.exists() and out_parquet.exists() and not force:
        return load_documents()

    golden_df = pd.read_csv(golden_path, encoding='utf-8', on_bad_lines='skip')
    sample_df = pd.read_csv(sample_path, encoding='utf-8', on_bad_lines='skip')

    merged = golden_df[['conversation_id', 'intent_label', 'intent_category', 'language', 'confidence', 'clean_text']].merge(
        sample_df[['conversation_id', 'conversation', 'message_count']], on='conversation_id', how='left'
    )
    merged = merged.copy()
    merged['conversation'] = merged['conversation'].fillna(merged['clean_text'])
    merged['customer_query'], merged['amazon_response'] = zip(*merged['clean_text'].map(_split_customer_and_amazon))
    merged['metadata'] = merged.apply(
        lambda row: json.dumps({
            'intent_label': row['intent_label'],
            'intent_category': row['intent_category'],
            'language': row['language'],
            'confidence': float(row['confidence']),
            'message_count': int(row['message_count']) if pd.notna(row['message_count']) else 0,
        }, ensure_ascii=False),
        axis=1,
    )
    merged['document_id'] = merged.apply(
        lambda row: str(row['conversation_id']) + '|' + str(row['intent_label']) + '|' + str(row['language']),
        axis=1,
    )

    docs = merged[[
        'document_id',
        'conversation_id',
        'intent_label',
        'intent_category',
        'customer_query',
        'amazon_response',
        'conversation',
        'clean_text',
        'language',
        'message_count',
        'metadata',
    ]].copy()
    docs = docs.reset_index(drop=True)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    docs.to_csv(out_csv, index=False, encoding='utf-8')
    docs.to_parquet(out_parquet, index=False)
    return docs


def generate_document_embeddings(force: bool = False, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', batch_size: int = 64) -> tuple[np.ndarray, pd.DataFrame]:
    """Generate embeddings for all knowledge documents and persist them with metadata."""
    if EMBEDDINGS_PATH.exists() and DOCUMENT_METADATA_PATH.exists() and not force:
        embeddings = np.load(EMBEDDINGS_PATH)
        metadata = pd.read_csv(DOCUMENT_METADATA_PATH, encoding='utf-8', on_bad_lines='skip')
        return embeddings, metadata

    docs = load_documents()
    texts = docs['clean_text'].fillna('').astype(str).tolist()
    model = SentenceTransformer(model_name, device='cpu')
    vectors = model.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype=np.float32)

    metadata = docs[[
        'document_id',
        'conversation_id',
        'intent_label',
        'intent_category',
        'language',
        'message_count',
    ]].copy()
    metadata['embedding_dimension'] = vectors.shape[1]
    metadata.to_csv(DOCUMENT_METADATA_PATH, index=False, encoding='utf-8')
    np.save(EMBEDDINGS_PATH, vectors.astype(np.float32))
    return vectors, metadata
