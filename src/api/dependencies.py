"""Dependency injection and singleton services for FastAPI."""

from __future__ import annotations

import logging
import traceback
from functools import lru_cache
from typing import Any

LOGGER = logging.getLogger("api.dependencies")


@lru_cache(maxsize=1)
def get_chatbot_singleton() -> dict[str, Any]:
    """
    Lazy singleton for SupportChatbot.

    Initializes only on the FIRST /chat request.
    After that, the chatbot is cached for all future requests.
    """

    LOGGER.info("Initializing chatbot singleton...")

    try:
        # Import only when needed
        from src.retrieval.retriever import load_index
        from src.chatbot.chatbot import SupportChatbot

        LOGGER.info("Loading FAISS index...")
        retriever_state = load_index()

        LOGGER.info("Creating SupportChatbot...")
        bot = SupportChatbot()

        LOGGER.info("Chatbot initialized successfully.")

        return {
            "chatbot": bot,
            "retriever_state": retriever_state,
        }

    except Exception as exc:
        LOGGER.error("Chatbot initialization FAILED")
        LOGGER.error(traceback.format_exc())

        raise RuntimeError(
            f"Chatbot initialization failed: {type(exc).__name__}: {exc}"
        ) from exc