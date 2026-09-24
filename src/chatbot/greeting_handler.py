from __future__ import annotations

import re
from typing import Any


class GreetingHandler:
    """Detects and handles greetings and casual conversation before retrieval."""

    # Greeting patterns - includes variations like "hii", "hiii", etc.
    GREETING_PATTERNS = {
        "hello": r"\bhello+\b",
        "hi": r"\bhi+\b",
        "hey": r"\bhey\b",
        "good morning": r"good\s+morning",
        "good afternoon": r"good\s+afternoon",
        "good evening": r"good\s+evening",
        "see you": r"see\s+you",
    }

    # Thank-you patterns
    THANK_YOU_PATTERNS = {
        "thanks": r"\bthanks\b",
        "thank you": r"thank\s+you",
    }

    # Goodbye patterns
    GOODBYE_PATTERNS = {
        "bye": r"\bbye\b",
        "goodbye": r"goodbye",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for pattern matching, including repeated letters."""
        # Convert to lowercase and strip whitespace
        normalized = text.lower().strip()

        # Normalize repeated letters (hii, hiii -> hi, hiiii -> hi, etc.)
        # Replace repeated characters (3+ times) with 2
        import re
        normalized = re.sub(r'([a-z])\1{2,}', r'\1\1', normalized)

        return normalized

    @classmethod
    def detect_greeting(cls, query: str) -> str | None:
        """
        Detect if query is a greeting.
        Returns the greeting type or None.
        """
        normalized = cls.normalize_text(query)

        for greeting_type, pattern in cls.GREETING_PATTERNS.items():
            if re.search(pattern, normalized):
                return greeting_type

        return None

    @classmethod
    def detect_thank_you(cls, query: str) -> str | None:
        """
        Detect if query is a thank-you message.
        Returns the thank-you type or None.
        """
        normalized = cls.normalize_text(query)

        for thank_type, pattern in cls.THANK_YOU_PATTERNS.items():
            if re.search(pattern, normalized):
                return thank_type

        return None

    @classmethod
    def detect_goodbye(cls, query: str) -> str | None:
        """
        Detect if query is a goodbye message.
        Returns the goodbye type or None.
        """
        normalized = cls.normalize_text(query)

        for goodbye_type, pattern in cls.GOODBYE_PATTERNS.items():
            if re.search(pattern, normalized):
                return goodbye_type

        return None

    @classmethod
    def is_greeting_or_casual(cls, query: str) -> bool:
        """Check if query is any greeting or casual conversation."""
        return (
            cls.detect_greeting(query) is not None
            or cls.detect_thank_you(query) is not None
            or cls.detect_goodbye(query) is not None
        )

    @classmethod
    def get_greeting_response(cls, query: str) -> dict[str, Any] | None:
        """
        Get a predefined response for greeting/casual conversation.
        Returns response dict or None if not a greeting.
        """
        # Check for greeting
        greeting = cls.detect_greeting(query)
        if greeting:
            response_text = cls._get_greeting_reply(greeting)
            return {
                "answer": response_text,
                "intent_label": "Greeting",
                "intent_category": "Greeting",
                "confidence": 1.0,
                "context": [],
                "is_greeting": True,
            }

        # Check for thank-you
        thank_you = cls.detect_thank_you(query)
        if thank_you:
            response_text = cls._get_thank_you_reply(thank_you)
            return {
                "answer": response_text,
                "intent_label": "Greeting",
                "intent_category": "Greeting",
                "confidence": 1.0,
                "context": [],
                "is_greeting": True,
            }

        # Check for goodbye
        goodbye = cls.detect_goodbye(query)
        if goodbye:
            response_text = cls._get_goodbye_reply(goodbye)
            return {
                "answer": response_text,
                "intent_label": "Greeting",
                "intent_category": "Greeting",
                "confidence": 1.0,
                "context": [],
                "is_greeting": True,
            }

        return None

    @staticmethod
    def _get_greeting_reply(greeting_type: str) -> str:
        """Get friendly greeting response."""
        responses = {
            "hello": "Hello! How can I assist you with your Amazon orders or account today?",
            "hi": "Hi there! I'm here to help with any questions about orders, returns, delivery, or your account.",
            "hey": "Hey! What can I help you with today?",
            "good morning": "Good morning! I hope you're having a great day. How can I help?",
            "good afternoon": "Good afternoon! Happy to assist. What brings you here?",
            "good evening": "Good evening! How can I help you out?",
        }
        return responses.get(greeting_type, "Hello! How can I help you?")

    @staticmethod
    def _get_thank_you_reply(thank_type: str) -> str:
        """Get friendly thank-you response."""
        responses = {
            "thanks": "You're welcome! Is there anything else I can help you with?",
            "thank you": "Happy to help! Feel free to reach out if you have any other questions.",
        }
        return responses.get(thank_type, "You're welcome!")

    @staticmethod
    def _get_goodbye_reply(goodbye_type: str) -> str:
        """Get friendly goodbye response."""
        responses = {
            "bye": "Goodbye! Have a great day, and thanks for reaching out!",
            "goodbye": "Take care! We're always here if you need help.",
        }
        return responses.get(goodbye_type, "Goodbye!")
