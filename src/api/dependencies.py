"""Dependency injection and singleton services for FastAPI."""

from __future__ import annotations

import logging
import threading
import traceback
from datetime import datetime, timezone
from typing import Any

LOGGER = logging.getLogger("api.dependencies")

_lock = threading.Lock()
_singleton: dict[str, Any] | None = None


def get_chatbot_singleton() -> dict[str, Any]:
    """
    Lazy, thread-safe singleton for SupportChatbot.
    Raises RuntimeError with a full traceback logged if initialization fails —
    the route layer converts this to HTTP 500 with the real exception message.
    """
    global _singleton
    if _singleton is not None:
        return _singleton

    with _lock:
        if _singleton is not None:
            return _singleton

        LOGGER.info("dependencies: initializing SupportChatbot singleton")
        t0 = datetime.now(timezone.utc)

        try:
            # Warm up the embedding model and FAISS index BEFORE constructing
            # the chatbot so the first /chat request never triggers a cold load.
            # On Render free tier (512 MB) loading both inside a request handler
            # exceeds the 30-second timeout and causes a 502.
            from src.retrieval.retriever import load_index
            LOGGER.info("dependencies: warming up FAISS index and embedding model")
            t_warm = datetime.now(timezone.utc)
            load_index()
            LOGGER.info(
                "dependencies: warm-up complete in %.2fs",
                (datetime.now(timezone.utc) - t_warm).total_seconds(),
            )

            from src.chatbot.chatbot import SupportChatbot

            LOGGER.info("dependencies: constructing SupportChatbot")
            bot = SupportChatbot()
            elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
            LOGGER.info("dependencies: SupportChatbot ready in %.2fs", elapsed)

            _singleton = {"chatbot": bot, "retriever_state": None}

        except Exception as exc:
            tb = traceback.format_exc()
            LOGGER.error(
                "dependencies: SupportChatbot init FAILED — %s: %s\nTraceback:\n%s",
                type(exc).__name__, exc, tb,
            )
            raise RuntimeError(
                f"Chatbot initialization failed — {type(exc).__name__}: {exc}"
            ) from exc

    return _singleton
