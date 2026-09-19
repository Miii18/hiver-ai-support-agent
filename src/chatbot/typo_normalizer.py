from __future__ import annotations

from difflib import SequenceMatcher
from typing import Optional


class TypoNormalizer:
    """Normalize common customer spelling mistakes before intent classification."""

    # Common misspellings mapped to correct terms
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
        "assisstant": "assistant",
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

        # Replace exact misspellings
        for misspelled, correct in TypoNormalizer.MISSPELLING_MAP.items():
            normalized = normalized.replace(misspelled, correct)

        return normalized

    @classmethod
    def fuzzy_normalize(cls, word: str, threshold: float = 0.8) -> Optional[str]:
        """
        Fuzzy match a word against known misspellings.
        Returns the correct term if similarity exceeds threshold.
        """
        word_lower = word.lower()

        if word_lower in cls.MISSPELLING_MAP:
            return cls.MISSPELLING_MAP[word_lower]

        best_match = None
        best_ratio = 0.0

        for misspelled, correct in cls.MISSPELLING_MAP.items():
            ratio = SequenceMatcher(None, word_lower, misspelled).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = correct

        return best_match
