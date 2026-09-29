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

# Resolve HF cache:
# HF_HOME environment variable wins.
# Fallback is platform-appropriate.
_DEFAULT_HF_CACHE = (
    Path(r"D:\AI\hf_cache")
    if os.name == "nt"
    else Path.home() / ".cache" / "huggingface"
)

HF_CACHE = Path(
    os.environ.get("HF_HOME", str(_DEFAULT_HF_CACHE))
)

try:
    HF_CACHE.mkdir(parents=True, exist_ok=True)
except OSError:
    HF_CACHE = Path.home() / ".cache" / "huggingface"
    HF_CACHE.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("HF_HOME", str(HF_CACHE))
os.environ.setdefault(
    "HUGGINGFACE_HUB_CACHE",
    str(HF_CACHE / "hub"),
)

# TRANSFORMERS_CACHE is deprecated but kept for older libraries.
os.environ.setdefault(
    "TRANSFORMERS_CACHE",
    str(HF_CACHE / "transformers"),
)

from sentence_transformers import SentenceTransformer  # noqa: E402


LOGGER = logging.getLogger("retriever")


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INDEX_PATH = (
    PROJECT_ROOT
    / "models"
    / "faiss"
    / "amazon_support.index"
)

INDEX_META_PATH = (
    PROJECT_ROOT
    / "models"
    / "faiss"
    / "index_metadata.json"
)

DOC_METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "knowledge_base"
    / "document_metadata.csv"
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# SINGLETON CACHE
# ============================================================

_lock = threading.RLock()

_MODEL_CACHE: SentenceTransformer | None = None

_INDEX_CACHE: dict[str, Any] | None = None


# ============================================================
# EMBEDDING MODEL
# ============================================================

def _get_model() -> SentenceTransformer:
    """
    Load the SentenceTransformer model only once.

    Thread-safe singleton.
    """

    global _MODEL_CACHE

    # Fast path:
    # model already loaded.
    if _MODEL_CACHE is not None:
        LOGGER.info(
            "retriever: embedding model served from cache"
        )
        return _MODEL_CACHE

    # First request:
    # only one thread is allowed to initialize the model.
    with _lock:

        if _MODEL_CACHE is not None:
            LOGGER.info(
                "retriever: embedding model served from cache"
            )
            return _MODEL_CACHE

        started_at = datetime.now(timezone.utc)

        LOGGER.info(
            "retriever: loading SentenceTransformer model=%s",
            MODEL_NAME,
        )

        try:
            model = SentenceTransformer(
                MODEL_NAME,
                device="cpu",
            )

            _MODEL_CACHE = model

            elapsed = (
                datetime.now(timezone.utc) - started_at
            ).total_seconds()

            LOGGER.info(
                "retriever: SentenceTransformer loaded in %.2fs",
                elapsed,
            )

            return _MODEL_CACHE

        except Exception:
            LOGGER.error(
                "retriever: SentenceTransformer loading FAILED"
            )
            LOGGER.error(traceback.format_exc())
            raise


# ============================================================
# FAISS INDEX
# ============================================================

def load_index() -> dict[str, Any]:
    """
    Load FAISS index, metadata and embedding model once.

    Subsequent calls return the exact same cached objects.
    """

    global _INDEX_CACHE

    # Fast path:
    # everything has already been loaded.
    if _INDEX_CACHE is not None:
        LOGGER.info(
            "retriever: load_index served from cache"
        )
        return _INDEX_CACHE

    # First initialization.
    with _lock:

        # Another request may have initialized it
        # while this thread was waiting for the lock.
        if _INDEX_CACHE is not None:
            LOGGER.info(
                "retriever: load_index served from cache"
            )
            return _INDEX_CACHE

        started_at = datetime.now(timezone.utc)

        LOGGER.info(
            "retriever: load_index starting"
        )

        # ----------------------------------------------------
        # Validate required files
        # ----------------------------------------------------

        if not INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {INDEX_PATH}"
            )

        if not DOC_METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Document metadata not found: {DOC_METADATA_PATH}"
            )

        # ----------------------------------------------------
        # Load FAISS index
        # ----------------------------------------------------

        LOGGER.info(
            "retriever: reading FAISS index from %s",
            INDEX_PATH,
        )

        index = faiss.read_index(
            str(INDEX_PATH)
        )

        # ----------------------------------------------------
        # Load document metadata
        # ----------------------------------------------------

        LOGGER.info(
            "retriever: reading document metadata from %s",
            DOC_METADATA_PATH,
        )

        documents = pd.read_csv(
            DOC_METADATA_PATH,
            encoding="utf-8",
            on_bad_lines="skip",
        )

        # ----------------------------------------------------
        # Load optional index metadata
        # ----------------------------------------------------

        index_meta: dict[str, Any] = {}

        if INDEX_META_PATH.exists():

            with INDEX_META_PATH.open(
                "r",
                encoding="utf-8",
            ) as fh:

                index_meta = json.load(fh)

        # ----------------------------------------------------
        # Load embedding model
        # ----------------------------------------------------

        LOGGER.info(
            "retriever: loading embedding model"
        )

        model = _get_model()

        # ----------------------------------------------------
        # Validate FAISS / metadata compatibility
        # ----------------------------------------------------

        if len(documents) == 0:
            LOGGER.warning(
                "retriever: document metadata contains 0 documents"
            )

        if index.d != model.get_sentence_embedding_dimension():
            raise ValueError(
                "Embedding dimension mismatch: "
                f"FAISS index dimension={index.d}, "
                f"model dimension="
                f"{model.get_sentence_embedding_dimension()}"
            )

        # ----------------------------------------------------
        # Build singleton cache
        # ----------------------------------------------------

        _INDEX_CACHE = {
            "index": index,
            "documents": documents,
            "model": model,
            "metadata": index_meta,
        }

        elapsed = (
            datetime.now(timezone.utc) - started_at
        ).total_seconds()

        LOGGER.info(
            "retriever: index loaded successfully — "
            "%d documents, dimension=%d, elapsed=%.2fs",
            len(documents),
            index.d,
            elapsed,
        )

        return _INDEX_CACHE


# ============================================================
# QUERY ENCODING
# ============================================================

def encode_query(query: str) -> np.ndarray:
    """
    Convert a query into a normalized embedding vector.
    """

    if not str(query).strip():
        raise ValueError(
            "Query cannot be empty"
        )

    model = _get_model()

    vector = model.encode(
        [str(query).strip()],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return np.asarray(
        vector,
        dtype=np.float32,
    ).reshape(1, -1)


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(
    query: str,
    top_k: int = 5,
) -> pd.DataFrame:
    """
    Retrieve the most similar conversations
    using FAISS cosine similarity.
    """

    if top_k <= 0:
        raise ValueError(
            "top_k must be positive"
        )

    query = str(query).strip()

    if not query:
        raise ValueError(
            "Query cannot be empty"
        )

    LOGGER.info(
        "retriever: retrieve query=%r top_k=%d",
        query[:80],
        top_k,
    )

    started_at = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # IMPORTANT:
    # This MUST use the cached load_index().
    # It must NOT manually reload FAISS/model.
    # --------------------------------------------------------

    try:

        index_data = load_index()

    except Exception as exc:

        LOGGER.error(
            "retriever: load_index failed — %s\n%s",
            exc,
            traceback.format_exc(),
        )

        raise

    index = index_data["index"]

    documents = index_data["documents"]

    model = index_data["model"]

    # --------------------------------------------------------
    # Encode query
    # --------------------------------------------------------

    try:

        LOGGER.info(
            "retriever: encoding query"
        )

        vector = model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        vector = np.asarray(
            vector,
            dtype=np.float32,
        ).reshape(1, -1)

    except Exception as exc:

        LOGGER.error(
            "retriever: embedding failed — %s\n%s",
            exc,
            traceback.format_exc(),
        )

        raise

    # --------------------------------------------------------
    # FAISS search
    # --------------------------------------------------------

    try:

        LOGGER.info(
            "retriever: FAISS search"
        )

        search_k = min(
            top_k,
            len(documents),
        )

        if search_k <= 0:

            LOGGER.warning(
                "retriever: no documents available"
            )

            return pd.DataFrame(
                columns=[
                    "conversation_id",
                    "intent_label",
                    "intent_category",
                    "customer_query",
                    "amazon_response",
                    "similarity_score",
                    "document_id",
                ]
            )

        scores, neighbor_ids = index.search(
            vector,
            search_k,
        )

    except Exception as exc:

        LOGGER.error(
            "retriever: FAISS search failed — %s\n%s",
            exc,
            traceback.format_exc(),
        )

        raise

    # --------------------------------------------------------
    # Convert results
    # --------------------------------------------------------

    rows: list[dict[str, Any]] = []

    for score, doc_idx in zip(
        scores[0],
        neighbor_ids[0],
    ):

        if doc_idx < 0:
            continue

        doc = documents.iloc[
            int(doc_idx)
        ].copy()

        rows.append(
            {
                "conversation_id": doc.get(
                    "conversation_id",
                    "",
                ),
                "intent_label": doc.get(
                    "intent_label",
                    "",
                ),
                "intent_category": doc.get(
                    "intent_category",
                    "",
                ),
                "customer_query": doc.get(
                    "customer_query",
                    "",
                ),
                "amazon_response": doc.get(
                    "amazon_response",
                    "",
                ),
                "similarity_score": float(
                    score
                ),
                "document_id": doc.get(
                    "document_id",
                    "",
                ),
            }
        )

    # --------------------------------------------------------
    # Empty result
    # --------------------------------------------------------

    result = pd.DataFrame(rows)

    if result.empty:

        LOGGER.warning(
            "retriever: no results returned "
            "for query=%r",
            query[:80],
        )

        return pd.DataFrame(
            columns=[
                "conversation_id",
                "intent_label",
                "intent_category",
                "customer_query",
                "amazon_response",
                "similarity_score",
                "document_id",
            ]
        )

    # --------------------------------------------------------
    # Sort by similarity
    # --------------------------------------------------------

    result = (
        result
        .sort_values(
            "similarity_score",
            ascending=False,
            kind="mergesort",
        )
        .reset_index(drop=True)
    )

    elapsed = (
        datetime.now(timezone.utc) - started_at
    ).total_seconds()

    LOGGER.info(
        "retriever: retrieve completed — "
        "%d results in %.2fs",
        len(result),
        elapsed,
    )

    return result