"""Dependency injection and singleton services for FastAPI."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

LOGGER = logging.getLogger("api.dependencies")


class DummyChatbot:
    """Fallback chatbot if real chatbot fails."""

    def __init__(self):
        self.memory = []

    def answer_query(self, query: str):
        return {
            "intent_label": "general_inquiry",
            "answer": "Chatbot is temporarily unavailable.",
            "confidence": 0.0,
            "context": [],
            "escalation": {},
            "escalation_triggered": False,
        }


@lru_cache(maxsize=1)
def get_chatbot_singleton() -> dict[str, Any]:
    """
    Lazy initialization of chatbot.
    FAISS index is NOT loaded during startup.
    """

    LOGGER.info("Initializing chatbot singleton...")

    try:
        from src.chatbot.chatbot import SupportChatbot

        bot = SupportChatbot()

        LOGGER.info("Chatbot initialized successfully.")

        return {
            "chatbot": bot,
            "retriever_state": None,
        }

    except Exception as exc:
        LOGGER.exception("Failed to initialize chatbot: %s", exc)

        return {
            "chatbot": DummyChatbot(),
            "retriever_state": None,
        }