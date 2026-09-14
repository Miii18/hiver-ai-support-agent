from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(text).lower()).strip()


class QueryClassifier:
    """Lightweight intent classifier that uses the Phase 5 canonical labels."""

    def __init__(self, intents_path: str | Path | None = None) -> None:
        self.intents_path = Path(intents_path) if intents_path else PROJECT_ROOT / 'data' / 'intents' / 'golden_intents.csv'
        self.intent_catalog = self._load_intents()

    def _load_intents(self) -> pd.DataFrame:
        if not self.intents_path.exists():
            return pd.DataFrame([
                {'intent_label': 'Customer Amazon Order', 'intent_category': 'Orders'},
                {'intent_label': 'Returns & Refunds', 'intent_category': 'Returns & Refunds'},
                {'intent_label': 'Prime Membership', 'intent_category': 'Subscriptions'},
                {'intent_label': 'Account & Login', 'intent_category': 'Account'},
                {'intent_label': 'Product Quality', 'intent_category': 'Product Quality'},
            ])
        data = pd.read_csv(self.intents_path, encoding='utf-8', on_bad_lines='skip')
        if 'intent_label' not in data.columns or 'intent_category' not in data.columns:
            return pd.DataFrame([
                {'intent_label': 'Customer Amazon Order', 'intent_category': 'Orders'},
                {'intent_label': 'Returns & Refunds', 'intent_category': 'Returns & Refunds'},
                {'intent_label': 'Prime Membership', 'intent_category': 'Subscriptions'},
                {'intent_label': 'Account & Login', 'intent_category': 'Account'},
                {'intent_label': 'Product Quality', 'intent_category': 'Product Quality'},
            ])
        return data[['intent_label', 'intent_category']].drop_duplicates().reset_index(drop=True)

    def classify(self, query: str) -> dict[str, str | float]:
        normalized = _normalize(query)
        if not normalized:
            return {'intent_label': 'Customer Amazon Order', 'intent_category': 'Orders', 'confidence': 0.0}

        keyword_map = {
            'Customer Amazon Order': ['order', 'delivery', 'shipping', 'package', 'track', 'shipment', 'where is', 'arrive', 'late'],
            'Returns & Refunds': ['refund', 'return', 'cancel', 'chargeback', 'replacement', 'reimburse', 'returning'],
            'Prime Membership': ['prime', 'membership', 'subscription', 'renew', 'trial'],
            'Account & Login': ['login', 'password', 'account', 'locked', 'sign in', 'access', 'email'],
            'Product Quality': ['damaged', 'broken', 'defective', 'wrong item', 'quality', 'missing'],
        }

        best_label = 'Customer Amazon Order'
        best_category = 'Orders'
        best_score = 0.0

        for _, row in self.intent_catalog.iterrows():
            label = str(row.get('intent_label', 'Customer Amazon Order'))
            category = str(row.get('intent_category', 'Orders'))
            keys = keyword_map.get(label, [])
            score = 0.0
            for keyword in keys:
                if keyword in normalized:
                    score += 1.0
            if label.lower() in normalized:
                score += 1.5
            if category.lower() in normalized:
                score += 0.5
            if score > best_score:
                best_score = score
                best_label = label
                best_category = category

        confidence = min(0.99, max(0.1, best_score / 4.0)) if best_score > 0 else 0.2
        return {'intent_label': best_label, 'intent_category': best_category, 'confidence': round(float(confidence), 4)}
