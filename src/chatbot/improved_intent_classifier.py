from __future__ import annotations

import re
from typing import Any


class ImprovedIntentClassifier:
    """Production-grade intent classifier with keyword-based detection and confidence scoring."""

    # Intent keywords for direct matching
    INTENT_KEYWORDS = {
        "Greeting": [
            "hello", "hi", "hey", "thanks", "thank you", "bye", "goodbye",
            "good morning", "good afternoon", "good evening"
        ],
        "Returns & Refunds": [
            "refund", "return", "replacement", "money back", "exchange",
            "cancel return", "reimburse", "chargeback", "reimbursement"
        ],
        "Delivery": [
            "delivery", "delivered", "package", "parcel", "shipping",
            "tracking", "late", "delayed", "where is", "track"
        ],
        "Orders": [
            "order status", "order", "purchase", "checkout", "bought",
            "where is my order", "order number"
        ],
        "Prime Membership": [
            "prime", "membership", "renewal", "subscription", "prime day",
            "cancel prime", "prime benefits"
        ],
        "Login & Authentication": [
            "password", "login", "otp", "verification", "account locked",
            "sign in", "forgot password", "access", "2fa", "two factor"
        ],
        "Promotions & Coupons": [
            "coupon", "promo", "discount", "offer", "code", "promotion",
            "not working", "invalid"
        ],
        "Technical Issue": [
            "app crash", "website not working", "error", "bug", "loading",
            "frozen", "not loading", "broken", "glitch", "crash"
        ],
    }

    # Display name mapping
    DISPLAY_NAME_MAP = {
        "Customer Amazon Order": "Orders",
        "Que Amazon Customer": "Returns & Refunds",
        "Amazon Customer Tn": "Prime Membership",
        "Amazon Customer Contest": "Promotions & Coupons",
        "Amazon Vous Customer": "Delivery",
        "Customer Amazon Die": "Login & Authentication",
        "Customer Amazon Que": "Technical Issue",
        "Returns & Refunds": "Returns & Refunds",
        "Delivery": "Delivery",
        "Orders": "Orders",
        "Prime Membership": "Prime Membership",
        "Login & Authentication": "Login & Authentication",
        "Promotions & Coupons": "Promotions & Coupons",
        "Technical Issue": "Technical Issue",
        "Greeting": "Greeting",
        "Other": "Other Support",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching."""
        return re.sub(r'[^a-z0-9\s]', ' ', text.lower()).strip()

    @classmethod
    def classify_by_keywords(cls, query: str) -> tuple[str, float] | None:
        """
        Classify query by keywords.
        Returns (intent_label, confidence) or None if no keyword match.
        """
        normalized = cls.normalize_text(query)
        best_match = None
        best_score = 0.0

        for intent_label, keywords in cls.INTENT_KEYWORDS.items():
            score = 0.0
            for keyword in keywords:
                if keyword in normalized:
                    # Exact phrase match gets higher score
                    if f" {keyword} " in f" {normalized} ":
                        score += 2.0
                    else:
                        score += 1.0

            if score > best_score:
                best_score = score
                best_match = intent_label

        if best_match and best_score > 0:
            # Confidence based on match strength
            if best_match == "Greeting":
                confidence = 1.0
            else:
                confidence = min(1.0, 0.9 + (best_score * 0.05))
            return (best_match, round(confidence, 2))

        return None

    @classmethod
    def get_display_name(cls, internal_label: str) -> str:
        """Map internal label to display name."""
        return cls.DISPLAY_NAME_MAP.get(internal_label, "Other Support")

    @classmethod
    def get_confidence_color(cls, confidence: float) -> str:
        """Get color badge for confidence level."""
        if confidence >= 0.8:
            return "green"
        elif confidence >= 0.6:
            return "yellow"
        else:
            return "red"

    @classmethod
    def get_low_confidence_message(cls, base_answer: str) -> str:
        """Return low confidence disclaimer."""
        return (
            "I found the closest available customer support guidance, but confidence is low. "
            "Please verify this matches your concern:\n\n" + base_answer
        )
