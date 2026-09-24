from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any


class TypoNormalizer:
    """Normalize common customer spelling mistakes."""

    MISSPELLING_MAP = {
        "retern": "return",
        "refnd": "refund",
        "pakage": "package",
        "delivary": "delivery",
        "passwrd": "password",
        "logn": "login",
        "membeship": "membership",
        "cupon": "coupon",
        "returm": "return",
        "retefund": "refund",
        "pacakge": "package",
        "deliery": "delivery",
        "passowrd": "password",
        "signin": "sign in",
        "singup": "sign up",
        "chekout": "checkout",
        "prodcut": "product",
        "orfer": "offer",
        "promocde": "promo code",
        "carge": "charge",
        "chaege": "charge",
        "custmer": "customer",
        "supprt": "support",
        "imte": "item",
        "recieved": "received",
        "recived": "received",
        "damged": "damaged",
        "defctive": "defective",
        "trakcing": "tracking",
        "shpping": "shipping",
        "brocken": "broken",
        "crashe": "crash",
        "isue": "issue",
        "problm": "problem",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text by replacing common misspellings."""
        normalized = text.lower()
        for misspelled, correct in TypoNormalizer.MISSPELLING_MAP.items():
            normalized = normalized.replace(misspelled, correct)
        return normalized


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
            "cancel return", "reimburse", "chargeback", "reimbursement",
            "damaged", "broken", "torn", "opened package", "defective",
            "cracked", "wrong item", "missing item", "received torn",
            "received damaged", "damaged product",
            "incorrect product", "ordered wrong", "wrong product",
        ],
        "Delivery": [
            "delivery", "delivered", "package", "parcel",
            "late delivery", "delayed delivery", "missing package",
            "lost package", "not delivered", "still not delivered",
            "estimated delivery", "delivery date", "shipment status"
        ],
        "Orders": [
            "order status", "track my order", "where is my order", "order number",
            "order", "purchase", "bought", "placed an order",
            "my order", "shipping status", "track", "tracking number"
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
            "frozen", "not loading", "broken", "glitch", "crash",
            "checkout", "checkout failed", "payment page", "unable to place order",
            "unable to place", "place order",
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
        """Normalize text for matching, including typo correction."""
        # First normalize punctuation and case
        normalized = re.sub(r'[^a-z0-9\s]', ' ', text.lower()).strip()
        # Then apply typo normalization
        return TypoNormalizer.normalize_text(normalized)

    # Intents that must win over any other match when their keywords are present
    _HIGH_PRIORITY_INTENTS = {"Returns & Refunds"}

    @classmethod
    def classify_by_keywords(cls, query: str) -> tuple[str, float] | None:
        """
        Classify query by keywords.
        Returns (intent_label, confidence) or None if no keyword match.
        """
        normalized = cls.normalize_text(query)
        scores: dict[str, float] = {}

        for intent_label, keywords in cls.INTENT_KEYWORDS.items():
            score = 0.0
            for keyword in keywords:
                if keyword in normalized:
                    # Exact phrase match gets higher score
                    if f" {keyword} " in f" {normalized} ":
                        score += 2.0
                    else:
                        score += 1.0
            if score > 0:
                scores[intent_label] = score

        if not scores:
            return None

        # High-priority intents win over any lower-priority match when they score > 0
        for hp_intent in cls._HIGH_PRIORITY_INTENTS:
            if hp_intent in scores:
                confidence = 1.0 if hp_intent == "Greeting" else 0.95
                return (hp_intent, round(confidence, 2))

        best_match = max(scores, key=lambda k: scores[k])
        confidence = 1.0 if best_match == "Greeting" else 0.95
        return (best_match, round(confidence, 2))

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
