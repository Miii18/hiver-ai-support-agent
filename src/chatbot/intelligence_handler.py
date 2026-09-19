from __future__ import annotations

import re
from typing import Any


class IntelligenceHandler:
    """Handles meta queries about the AI system without retrieval."""

    # AI identity patterns
    IDENTITY_PATTERNS = {
        "who_are_you": r"(who\s+are\s+you|who\s+is\s+this|who\s+am\s+i\s+talking\s+to|introduce\s+yourself)",
        "what_are_you": r"(what\s+are\s+you|what\s+is\s+this)",
        "tell_about_yourself": r"(tell\s+me\s+about\s+yourself|tell\s+me\s+about\s+you|about\s+yourself)",
        "are_you_ai": r"(are\s+you\s+an?\s+ai|are\s+you\s+artificial|are\s+you\s+human)",
    }

    # Capability patterns
    CAPABILITY_PATTERNS = {
        "what_can_help": r"(what\s+can\s+you\s+help\s+me\s+with|what\s+can\s+you\s+do|what\s+features|what\s+support)",
        "amazon_orders": r"(can\s+you\s+help\s+with.*order|help\s+with.*amazon|amazon\s+order)",
    }

    # Knowledge base patterns
    KNOWLEDGE_BASE_PATTERNS = {
        "knowledge_base": r"(knowledge\s+base|trained|training\s+data|what\s+data)",
    }

    # Confidence patterns
    CONFIDENCE_PATTERNS = {
        "confidence_score": r"(confidence\s+score|confidence|how\s+confident|why.*low\s+confidence)",
    }

    # Sources patterns
    SOURCES_PATTERNS = {
        "show_sources": r"(show.*source|previous\s+source|what\s+source|retrieved)",
    }

    # Out-of-scope patterns
    OUT_OF_SCOPE_PATTERNS = {
        "joke": r"(tell\s+me\s+a\s+joke|joke|funny)",
        "weather": r"(weather|temperature|forecast|rain)",
        "code": r"(write\s+code|write\s+python|code\s+example|programming)",
        "general": r"(general\s+question|not\s+amazon|not\s+about\s+amazon)",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for pattern matching."""
        return text.lower().strip()

    @classmethod
    def detect_ai_identity(cls, query: str) -> str | None:
        """Detect if query asks about AI identity. Returns identity type or None."""
        normalized = cls.normalize_text(query)
        for identity_type, pattern in cls.IDENTITY_PATTERNS.items():
            if re.search(pattern, normalized):
                return identity_type
        return None

    @classmethod
    def detect_capability_query(cls, query: str) -> str | None:
        """Detect if query asks about capabilities. Returns query type or None."""
        normalized = cls.normalize_text(query)
        for query_type, pattern in cls.CAPABILITY_PATTERNS.items():
            if re.search(pattern, normalized):
                return query_type
        return None

    @classmethod
    def detect_knowledge_base_query(cls, query: str) -> str | None:
        """Detect if query asks about knowledge base. Returns query type or None."""
        normalized = cls.normalize_text(query)
        for query_type, pattern in cls.KNOWLEDGE_BASE_PATTERNS.items():
            if re.search(pattern, normalized):
                return query_type
        return None

    @classmethod
    def detect_confidence_query(cls, query: str) -> str | None:
        """Detect if query asks about confidence. Returns query type or None."""
        normalized = cls.normalize_text(query)
        for query_type, pattern in cls.CONFIDENCE_PATTERNS.items():
            if re.search(pattern, normalized):
                return query_type
        return None

    @classmethod
    def detect_sources_query(cls, query: str) -> str | None:
        """Detect if query asks about retrieved sources. Returns query type or None."""
        normalized = cls.normalize_text(query)
        for query_type, pattern in cls.SOURCES_PATTERNS.items():
            if re.search(pattern, normalized):
                return query_type
        return None

    @classmethod
    def detect_out_of_scope(cls, query: str) -> str | None:
        """Detect if query is outside Amazon support scope. Returns scope type or None."""
        normalized = cls.normalize_text(query)
        for scope_type, pattern in cls.OUT_OF_SCOPE_PATTERNS.items():
            if re.search(pattern, normalized):
                return scope_type
        return None

    @classmethod
    def is_meta_query(cls, query: str) -> bool:
        """Check if query is a meta query (about the system, not support)."""
        return bool(
            cls.detect_ai_identity(query)
            or cls.detect_capability_query(query)
            or cls.detect_knowledge_base_query(query)
            or cls.detect_confidence_query(query)
            or cls.detect_sources_query(query)
            or cls.detect_out_of_scope(query)
        )

    @staticmethod
    def get_identity_response() -> str:
        """Get AI identity response."""
        return (
            "I'm Hiver AI Support Agent, an intelligent customer support assistant powered by "
            "retrieval-augmented generation. I'm designed to help Amazon customers with orders, "
            "delivery, returns, refunds, Prime membership, account access, promotions, and technical issues. "
            "I use advanced natural language understanding to find the most relevant support guidance from "
            "a knowledge base of thousands of customer support conversations."
        )

    @staticmethod
    def get_capability_response() -> str:
        """Get capability response."""
        return (
            "I can help you with the following Amazon support categories:\n\n"
            "• Orders - Track order status, view details, modify orders\n"
            "• Delivery - Track packages, check shipping status, resolve late deliveries\n"
            "• Returns & Refunds - Initiate returns, check refund status\n"
            "• Prime Membership - Manage subscription, view benefits\n"
            "• Login & Authentication - Reset password, enable 2FA\n"
            "• Promotions & Coupons - Troubleshoot coupon codes, view offers\n"
            "• Technical Issues - Resolve app crashes, website problems\n\n"
            "Just ask me about any of these topics, and I'll provide detailed guidance!"
        )

    @staticmethod
    def get_knowledge_base_response() -> str:
        """Get knowledge base response."""
        return (
            "My knowledge base contains 10,000 Amazon customer support conversations. "
            "I use SentenceTransformer embeddings to encode both your question and historical support cases "
            "into numerical vectors. These are then searched using FAISS (Facebook AI Similarity Search) "
            "to find the most relevant cases. This retrieval-augmented generation (RAG) workflow allows me "
            "to provide accurate, grounded responses based on real customer support patterns rather than "
            "generic guidance."
        )

    @staticmethod
    def get_confidence_response() -> str:
        """Get confidence score explanation."""
        return (
            "My confidence score (0-100%) indicates how certain I am about my response. "
            "Confidence is calculated based on: (1) how well your question matches keywords for specific support categories, "
            "(2) how similar your question is to cases in my knowledge base, and (3) the relevance of retrieved sources. "
            "Scores of 80%+ (green) indicate high confidence, 60-79% (yellow) indicate moderate confidence, "
            "and below 60% (red) indicate low confidence. When confidence is very low (<40%), I'll add a disclaimer. "
            "If you see a low confidence score, feel free to provide more details or clarify your question."
        )

    @staticmethod
    def get_out_of_scope_response() -> str:
        """Get out-of-scope response."""
        return (
            "I'm designed specifically for Amazon customer support questions. "
            "I can help with orders, delivery, refunds, Prime membership, login issues, promotions, and technical support. "
            "For other topics or questions outside the Amazon support domain, I won't be able to assist effectively. "
            "Please feel free to ask me any Amazon-related questions!"
        )

    @staticmethod
    def format_sources_response(sources: list[dict[str, Any]]) -> str:
        """Format retrieved sources for display."""
        if not sources:
            return (
                "No sources have been retrieved yet in this conversation. "
                "Ask me an Amazon support question, and I'll retrieve relevant customer support cases for you!"
            )

        response = "Here are the most recent sources retrieved from my knowledge base:\n\n"
        for idx, source in enumerate(sources[:3], 1):
            conversation_id = source.get("conversation_id", "Unknown")
            similarity = source.get("similarity_score", 0.0)
            response += f"{idx}. Conversation ID: {conversation_id}\n"
            response += f"   Relevance: {similarity:.0%}\n\n"

        return response
