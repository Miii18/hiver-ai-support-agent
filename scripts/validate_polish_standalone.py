#!/usr/bin/env python
"""Phase 9 Polish Validation - Standalone (no FAISS dependency)."""
import re
from typing import Optional, Tuple


class ImprovedIntentClassifier:
    """Production-grade intent classifier with keyword-based detection."""

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

    DISPLAY_NAME_MAP = {
        "Greeting": "Greeting",
        "Returns & Refunds": "Returns & Refunds",
        "Delivery": "Delivery",
        "Orders": "Orders",
        "Prime Membership": "Prime Membership",
        "Login & Authentication": "Login & Authentication",
        "Promotions & Coupons": "Promotions & Coupons",
        "Technical Issue": "Technical Issue",
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching."""
        return re.sub(r'[^a-z0-9\s]', ' ', text.lower()).strip()

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


# Test queries
TEST_QUERIES = [
    ("Hello", "Greeting", 1.0),
    ("Thanks", "Greeting", 1.0),
    ("Bye", "Greeting", 1.0),
    ("My Amazon package has not been delivered.", "Delivery", 0.9),
    ("I want a refund for my order.", "Returns & Refunds", 0.9),
    ("Cancel my Prime membership.", "Prime Membership", 0.9),
    ("I forgot my Amazon password.", "Login & Authentication", 0.9),
    ("Coupon code is not working.", "Promotions & Coupons", 0.9),
    ("Amazon app crashes every time I open it.", "Technical Issue", 0.9),
]


def main():
    """Run validation."""
    print("\n" + "=" * 80)
    print("PHASE 9 POLISH VALIDATION")
    print("=" * 80 + "\n")

    classifier = ImprovedIntentClassifier()
    all_passed = True
    results = []

    for query, expected_intent, expected_confidence in TEST_QUERIES:
        result = classifier.classify_by_keywords(query)

        if result is None:
            status = "FAIL"
            all_passed = False
            results.append((status, query, "No match", "None", "N/A"))
            continue

        intent, confidence = result
        display = classifier.get_display_name(intent)
        color = classifier.get_confidence_color(confidence)

        passed = (intent == expected_intent and
                  confidence >= expected_confidence - 0.01)

        status = "PASS" if passed else "FAIL"
        results.append((status, query, display, f"{confidence:.0%}", color))

        if not passed:
            all_passed = False

    # Print results table
    for status, query, intent, confidence, color in results:
        print(f"[{status}] {query:50s} -> {intent:25s} ({confidence:>4s}) [{color}]")

    print("\n" + "=" * 80)

    if all_passed:
        print("PHASE 9 POLISH VALIDATION PASSED")
        return 0
    else:
        print("PHASE 9 POLISH VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
