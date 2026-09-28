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
    Lazy singleton. Initializes chatbot only on the first /chat request.
    """

    LOGGER.info("Initializing chatbot singleton...")

    try:
        from src.chatbot.chatbot import SupportChatbot

        # DO NOT call load_index() here.
        # SupportChatbot should initialize it internally when needed.
        bot = SupportChatbot()

        LOGGER.info("Chatbot initialized successfully.")

        return {
            "chatbot": bot,
            "retriever_state": None,
        }

    except Exception as exc:
        LOGGER.error("Chatbot initialization FAILED")
        LOGGER.error(traceback.format_exc())

        raise RuntimeError(
            f"Chatbot initialization failed: {type(exc).__name__}: {exc}"
        ) from exc