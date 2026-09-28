from __future__ import annotations

import json
import logging
import os
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import faiss
import numpy as np
import pandas as pd

# Resolve HF cache: HF_HOME env var wins; fallback is platform-appropriate.
_DEFAULT_HF_CACHE = (
    Path(r"D:\AI\hf_cache") if os.name == "nt"
    else Path.home() / ".cache" / "huggingface"
)
HF_CACHE = Path(os.environ.get("HF_HOME", str(_DEFAULT_HF_CACHE)))
try:
    HF_CACHE.mkdir(parents=True, exist_ok=True)
except OSError:
    HF_CACHE = Path.home() / ".cache" / "huggingface"
    HF_CACHE.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("HF_HOME", str(HF_CACHE))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(HF_CACHE / "hub"))
# TRANSFORMERS_CACHE is deprecated but kept for older libs still reading it.
os.environ.setdefault("TRANSFORMERS_CACHE", str(HF_CACHE / "transformers"))

from sentence_transformers import SentenceTransformer  # noqa: E402

LOGGER = logging.getLogger("retriever")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_ROOT / "models" / "faiss" / "amazon_support.index"
INDEX_META_PATH = PROJECT_ROOT / "models" / "faiss" / "index_metadata.json"
DOC_METADATA_PATH = PROJECT_ROOT / "data" / "knowledge_base" / "document_metadata.csv"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- Module-level singletons (loaded once, thread-safe) ---
_lock = threading.Lock()
_MODEL_CACHE: SentenceTransformer | None = None
_INDEX_CACHE: dict[str, Any] | None = None


def _get_model() -> SentenceTransformer:
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        LOGGER.debug("retriever: embedding model served from cache")
        return _MODEL_CACHE
    with _lock:
        if _MODEL_CACHE is not None:
            LOGGER.debug("retriever: embedding model served from cache")
            return _MODEL_CACHE
        t0 = datetime.now(timezone.utc)
        LOGGER.info("retriever: loading SentenceTransformer model=%s (first time)", MODEL_NAME)
        _MODEL_CACHE = SentenceTransformer(MODEL_NAME, device="cpu")
        elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
        LOGGER.info("retriever: SentenceTransformer loaded in %.2fs", elapsed)
    return _MODEL_CACHE


def load_index() -> dict[str, Any]:
    """Load the FAISS index once and return the cached singleton."""
    global _INDEX_CACHE
    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    with _lock:
        if _INDEX_CACHE is not None:
            return _INDEX_CACHE

        t0 = datetime.now(timezone.utc)
        LOGGER.info("retriever: load_index starting")

        if not INDEX_PATH.exists():
            raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")
        if not DOC_METADATA_PATH.exists():
            raise FileNotFoundError(f"Document metadata not found: {DOC_METADATA_PATH}")

        LOGGER.info("retriever: reading FAISS index from %s", INDEX_PATH)
        index = faiss.read_index(str(INDEX_PATH))

        LOGGER.info("retriever: reading document metadata from %s", DOC_METADATA_PATH)
        metadata = pd.read_csv(DOC_METADATA_PATH, encoding="utf-8", on_bad_lines="skip")

        index_meta: dict = {}
        if INDEX_META_PATH.exists():
            with INDEX_META_PATH.open("r", encoding="utf-8") as fh:
                index_meta = json.load(fh)

        LOGGER.info("retriever: loading embedding model")
        model = _get_model()

        elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
        LOGGER.info(
            "retriever: index loaded — %d documents, dimension=%d, elapsed=%.2fs",
            len(metadata), index.d, elapsed,
        )

        _INDEX_CACHE = {
            "index": index,
            "documents": metadata,
            "model": model,
            "metadata": index_meta,
        }

    return _INDEX_CACHE


def encode_query(query: str) -> np.ndarray:
    model = _get_model()
    vector = model.encode([str(query).strip()], convert_to_numpy=True, normalize_embeddings=True)
    return np.asarray(vector, dtype=np.float32).reshape(1, -1)


def retrieve(query: str, top_k: int = 5) -> pd.DataFrame:
    """Retrieve the most similar conversations using FAISS cosine similarity."""
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    LOGGER.info("retriever: retrieve query=%r top_k=%d", query[:80], top_k)
    t0 = datetime.now(timezone.utc)

    try:
        index_data = load_index()
    except Exception as exc:
        LOGGER.error("retriever: load_index failed — %s\n%s", exc, traceback.format_exc())
        raise

    index = index_data["index"]
    documents = index_data["documents"]
    model = index_data["model"]

    try:
        LOGGER.info("retriever: encoding query")
        vector = model.encode([str(query).strip()], convert_to_numpy=True, normalize_embeddings=True)
        vector = np.asarray(vector, dtype=np.float32).reshape(1, -1)
    except Exception as exc:
        LOGGER.error("retriever: embedding failed — %s\n%s", exc, traceback.format_exc())
        raise

    try:
        LOGGER.info("retriever: FAISS search")
        scores, neighbor_ids = index.search(vector, min(top_k, len(documents)))
    except Exception as exc:
        LOGGER.error("retriever: FAISS search failed — %s\n%s", exc, traceback.format_exc())
        raise

    rows: list[dict[str, Any]] = []
    for score, doc_idx in zip(scores[0], neighbor_ids[0]):
        if doc_idx < 0:
            continue
        doc = documents.iloc[int(doc_idx)].copy()
        rows.append({
            "conversation_id": doc.get("conversation_id", ""),
            "intent_label": doc.get("intent_label", ""),
            "intent_category": doc.get("intent_category", ""),
            "customer_query": doc.get("customer_query", ""),
            "amazon_response": doc.get("amazon_response", ""),
            "similarity_score": float(score),
            "document_id": doc.get("document_id", ""),
        })

    result = pd.DataFrame(rows)
    if result.empty:
        LOGGER.warning("retriever: no results returned for query=%r", query[:80])
        return pd.DataFrame(columns=[
            "conversation_id", "intent_label", "intent_category",
            "customer_query", "amazon_response", "similarity_score", "document_id",
        ])

    result = result.sort_values("similarity_score", ascending=False, kind="mergesort").reset_index(drop=True)
    elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
    LOGGER.info("retriever: retrieve completed — %d results in %.2fs", len(result), elapsed)
    return result
