from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chatbot.memory import ConversationMemory
from src.chatbot.prompt_builder import PromptBuilder
from src.chatbot.query_classifier import QueryClassifier
from src.chatbot.response_formatter import ResponseFormatter
from src.retrieval.retriever import retrieve


class SupportChatbot:
    """Production-style retrieval augmented generation assistant for support conversations."""

    def __init__(self, top_k: int = 5, memory_limit: int = 6) -> None:
        self.top_k = top_k
        self.memory = ConversationMemory(max_turns=memory_limit)
        self.classifier = QueryClassifier()
        self.prompt_builder = PromptBuilder()

    def _grounded_answer(self, query: str, context: list[dict]) -> str:
        if not context:
            return 'I could not find a closely related support case in the knowledge base, but here are general steps: verify the order status, review the tracked shipping details, and contact support if the issue persists.'

        selected = context[0]
        customer = str(selected.get('customer_query') or selected.get('conversation', '')).strip()
        amazon = str(selected.get('amazon_response') or selected.get('response', '')).strip()
        if customer and amazon:
            return (
                f'Based on similar cases, the most relevant guidance is: "{amazon[:220]}". '
                'A good next step is to verify the order status in the tracking link and follow up with support if the delivery remains unresolved.'
            )
        if customer:
            return f'Looking at similar customer issues, the pattern suggests checking the order details and confirming the delivery timeline before contacting support: "{customer[:220]}".'
        return 'I found similar customer support guidance and recommend checking the shipping status, confirming the order details, and escalating if the issue persists.'

    def answer_query(self, query: str) -> dict:
        intent = self.classifier.classify(query)
        retrieved = retrieve(str(query), top_k=self.top_k)
        context_rows = []
        for _, row in retrieved.iterrows():
            context_rows.append({
                'conversation_id': row.get('conversation_id', ''),
                'customer_query': row.get('customer_query', ''),
                'amazon_response': row.get('amazon_response', ''),
                'intent_label': row.get('intent_label', intent['intent_label']),
                'similarity_score': float(row.get('similarity_score', 0.0)),
            })

        memory_context = self.memory.get_recent_context()
        memory_summary = ' | '.join(f"{entry['role']}: {entry['content']}" for entry in memory_context)
        prompt = self.prompt_builder.build_prompt(
            query=query,
            context=context_rows,
            intent_label=str(intent['intent_label']),
            memory_context=memory_summary,
        )

        answer = self._grounded_answer(query, context_rows)
        self.memory.add_turn('user', query)
        self.memory.add_turn('assistant', answer)

        return ResponseFormatter.format_response(
            answer=answer,
            intent_label=str(intent['intent_label']),
            intent_category=str(intent['intent_category']),
            confidence=float(intent['confidence']),
            context=context_rows,
        )
