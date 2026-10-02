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
        "Damaged Item Report": [
            "damaged", "defective", "broken", "cracked", "torn", "ripped",
            "crushed", "dented", "scratched", "ruined", "damaged product",
            "item arrived damaged", "received damaged", "received torn",
            "received a damaged", "received damaged product", "damaged item",
            "broken item", "defective item", "item is damaged",
        ],
        "Payment Failed — Money Still Deducted": [
            "payment failed", "payment fail", "failed payment", "money deducted",
            "amount deducted", "deducted but", "deducted from", "money was deducted",
            "amount was deducted", "balance deducted", "payment declined",
            "payment failed but money was deducted", "charged but order failed",
        ],
        "Update Delivery Address": [
            "update delivery address", "change shipping address", "change address",
            "update address", "shipping address", "change my delivery address",
            "change delivery address", "change my address", "change the delivery address",
            "modify delivery address", "modify my address", "wrong address",
        ],
        "Wrong Item Received": [
            "wrong item", "incorrect product", "incorrect item", "ordered wrong",
            "wrong product delivered", "wrong product", "received wrong product",
            "received the wrong product", "wrong product and i want a refund",
            "received incorrect", "sent wrong item",
        ],
        "Exchange Request": [
            "exchange my", "exchange this", "replace with another", "exchange product",
            "exchange this product", "swap for another", "exchange", "replace size",
            "swap item", "exchange item",
        ],
        "Delivery Partner Contact": [
            "delivery agent", "delivery person", "delivery partner", "delivery man",
            "delivery woman", "contact the delivery agent", "contact delivery agent",
            "contact delivery partner", "reach delivery agent", "call delivery agent",
            "driver phone", "call delivery driver",
        ],
        "Returns & Refunds": [
            "refund", "return", "replacement", "money back",
            "cancel return", "reimburse", "chargeback", "reimbursement",
            "missing item", "want a refund", "return my order",
            "refund for my purchase", "want to return", "refund request",
            "return request",
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
            "password", "login", "log in", "otp", "verification", "account locked",
            "sign in", "forgot password", "access", "2fa", "two factor",
            "cant log in", "can t log in", "cannot log in", "cant sign in",
            "can t sign in", "account access", "locked out", "locked account",
        ],
        "Promotions & Coupons": [
            "coupon", "promo", "discount", "offer", "code", "promotion",
            "not working", "invalid"
        ],
        "Technical Issue": [
            "app crash", "website not working", "error", "bug", "loading",
            "frozen", "not loading", "glitch", "crash",
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
        "Damaged Item Report": "Damaged Item Report",
        "Payment Failed — Money Still Deducted": "Payment Failed — Money Still Deducted",
        "Update Delivery Address": "Update Delivery Address",
        "Wrong Item Received": "Wrong Item Received",
        "Exchange Request": "Exchange Request",
        "Delivery Partner Contact": "Delivery Partner Contact",
        "Out of Scope": "Out of Scope",
        "System Info": "System Info",
        "Other": "Other Support",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching, including typo correction."""
        # First normalize punctuation and case
        normalized = re.sub(r'[^a-z0-9\s]', ' ', text.lower()).strip()
        # Then apply typo normalization
        return TypoNormalizer.normalize_text(normalized)

    # Priority order for intent matching: specific domains first, then general ones
    _PRIORITY_ORDER = [
        "Greeting",
        "Damaged Item Report",
        "Payment Failed — Money Still Deducted",
        "Wrong Item Received",
        "Exchange Request",
        "Update Delivery Address",
        "Delivery Partner Contact",
        "Returns & Refunds",
        "Delivery",
        "Orders",
        "Prime Membership",
        "Login & Authentication",
        "Promotions & Coupons",
        "Technical Issue",
    ]

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
                    # Longer phrase matches get higher specificity weight
                    word_count = len(keyword.split())
                    exact_phrase = f" {keyword} " in f" {normalized} "
                    multiplier = 2.0 if exact_phrase else 1.0
                    score += (word_count * 2.0) * multiplier
            if score > 0:
                scores[intent_label] = score

        if not scores:
            return None

        # Check in priority order if specific domain matches have matched
        max_score = max(scores.values())
        for priority_intent in cls._PRIORITY_ORDER:
            if priority_intent in scores and scores[priority_intent] >= max_score * 0.5:
                confidence = 1.0 if priority_intent == "Greeting" else 0.95
                return (priority_intent, round(confidence, 2))

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
