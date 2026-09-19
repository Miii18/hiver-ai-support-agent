#!/usr/bin/env python
"""Phase 9.6 Final QA Fixes - Standalone validation (no FAISS dependency)."""
import re
from difflib import SequenceMatcher
from typing import Optional, Tuple


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
        "damged": "damaged",
        "defctive": "defective",
        "brocken": "broken",
        "recieved": "received",
        "recived": "received",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text by replacing common misspellings."""
        normalized = text.lower()
        for misspelled, correct in TypoNormalizer.MISSPELLING_MAP.items():
            normalized = normalized.replace(misspelled, correct)
        return normalized


class ImprovedIntentClassifier:
    """Production-grade intent classifier with typo normalization and damaged product detection."""

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
            "received damaged", "damaged product"
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

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching, including typo correction."""
        normalized = re.sub(r'[^a-z0-9\s]', ' ', text.lower()).strip()
        return TypoNormalizer.normalize_text(normalized)

    @classmethod
    def classify_by_keywords(cls, query: str) -> Optional[Tuple[str, float]]:
        """Classify query by keywords. Returns (intent_label, confidence) or None."""
        normalized = cls.normalize_text(query)
        best_match = None
        best_score = 0.0

        for intent_label, keywords in cls.INTENT_KEYWORDS.items():
            score = 0.0
            for keyword in keywords:
                if keyword in normalized:
                    if f" {keyword} " in f" {normalized} ":
                        score += 2.0
                    else:
                        score += 1.0

            if score > best_score:
                best_score = score
                best_match = intent_label

        if best_match and best_score > 0:
            if best_match == "Greeting":
                confidence = 1.0
            else:
                confidence = min(1.0, 0.9 + (best_score * 0.05))
            return (best_match, round(confidence, 2))

        return None


# Test queries
TEST_QUERIES = [
    ("i want to retern my product", "Returns & Refunds"),
    ("received torn packet", "Returns & Refunds"),
    ("refund not received", "Returns & Refunds"),
    ("broken product", "Returns & Refunds"),
    ("wrong item delivered", "Returns & Refunds"),
    ("My Amazon package has not been delivered.", "Delivery"),
    ("I forgot my Amazon password.", "Login & Authentication"),
]


def main():
    """Run validation."""
    print("\n" + "=" * 80)
    print("PHASE 9.6 FINAL QA FIXES VALIDATION")
    print("=" * 80 + "\n")

    classifier = ImprovedIntentClassifier()
    all_passed = True
    results = []

    for query, expected_intent in TEST_QUERIES:
        result = classifier.classify_by_keywords(query)

        if result is None:
            status = "FAIL"
            intent = "No match"
            confidence = 0.0
            all_passed = False
        else:
            intent, confidence = result
            status = "PASS" if intent == expected_intent else "FAIL"
            if intent != expected_intent:
                all_passed = False

        results.append((status, query, intent, f"{confidence:.0%}"))

    # Print results table
    for status, query, intent, confidence in results:
        print(f"[{status}] {query:45s} -> {intent:25s} ({confidence:>4s})")

    print("\n" + "=" * 80)

    if all_passed:
        print("PHASE 9.6 FINAL QA FIXES COMPLETED")
        return 0
    else:
        print("PHASE 9.6 FINAL QA FIXES FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
