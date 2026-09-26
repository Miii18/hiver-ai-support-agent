"""Dependency injection and singleton services for FastAPI."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

LOGGER = logging.getLogger("api.dependencies")


@lru_cache(maxsize=1)
def get_chatbot_singleton() -> dict[str, Any]:
    """
    Lazily initialize the chatbot and retriever only once.
    This prevents Render from crashing during startup.
    """

    LOGGER.info("Initializing chatbot singleton and loading retriever/index...")

    try:
        from src.chatbot.chatbot import SupportChatbot
        from src.retrieval.retriever import load_index

        bot = SupportChatbot()

        retriever_state = None
        try:
            retriever_state = load_index()
            if retriever_state:
                LOGGER.info("Retriever loaded successfully.")
        except Exception as exc:
            LOGGER.exception("Failed to load FAISS index: %s", exc)
            retriever_state = None

        return {
            "chatbot": bot,
            "retriever_state": retriever_state,
        }

    except Exception as exc:
        LOGGER.exception("Failed to initialize chatbot: %s", exc)

        class DummyChatbot:
            def __init__(self):
                self.memory = []

            def answer_query(self, query: str):
                return {
                    "intent_label": "general_inquiry",
                    "answer": "Chatbot initialization failed. Please try again later.",
                    "confidence": 0.0,
                    "context": [],
                    "escalation": {},
                    "escalation_triggered": False,
                }

        return {
            "chatbot": DummyChatbot(),
            "retriever_state": None,
        }