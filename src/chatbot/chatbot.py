from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chatbot.greeting_handler import GreetingHandler
from src.chatbot.improved_intent_classifier import ImprovedIntentClassifier
from src.chatbot.intelligence_handler import IntelligenceHandler
from src.chatbot.memory import ConversationMemory
from src.chatbot.prompt_builder import PromptBuilder
from src.chatbot.query_classifier import QueryClassifier
from src.chatbot.response_formatter import ResponseFormatter
from src.chatbot.response_template_builder import ResponseTemplateBuilder
from src.retrieval.retriever import retrieve


class SupportChatbot:
    """Production-style retrieval augmented generation assistant for support conversations."""

    def __init__(self, top_k: int = 5, memory_limit: int = 6) -> None:
        self.top_k = top_k
        self.memory = ConversationMemory(max_turns=memory_limit)
        self.classifier = QueryClassifier()
        self.improved_classifier = ImprovedIntentClassifier()
        self.prompt_builder = PromptBuilder()
        self.greeting_handler = GreetingHandler()
        self.intelligence_handler = IntelligenceHandler()

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
        """Answer user query with greeting detection and improved intent classification."""
        # Check for meta queries (AI identity, capabilities, knowledge base, etc.) first
        if IntelligenceHandler.detect_ai_identity(query):
            answer = IntelligenceHandler.get_identity_response()
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer)
            return ResponseFormatter.format_response(
                answer=answer,
                intent_label='System Info',
                intent_category='System Info',
                confidence=1.0,
                context=[],
            )

        if IntelligenceHandler.detect_capability_query(query):
            answer = IntelligenceHandler.get_capability_response()
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer)
            return ResponseFormatter.format_response(
                answer=answer,
                intent_label='System Info',
                intent_category='System Info',
                confidence=1.0,
                context=[],
            )

        if IntelligenceHandler.detect_knowledge_base_query(query):
            answer = IntelligenceHandler.get_knowledge_base_response()
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer)
            return ResponseFormatter.format_response(
                answer=answer,
                intent_label='System Info',
                intent_category='System Info',
                confidence=1.0,
                context=[],
            )

        if IntelligenceHandler.detect_confidence_query(query):
            answer = IntelligenceHandler.get_confidence_response()
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer)
            return ResponseFormatter.format_response(
                answer=answer,
                intent_label='System Info',
                intent_category='System Info',
                confidence=1.0,
                context=[],
            )

        if IntelligenceHandler.detect_sources_query(query):
            # Get most recent sources from memory
            recent_sources = []
            for turn in reversed(self.memory.get_history()):
                if turn.get('role') == 'assistant' and turn.get('sources'):
                    recent_sources = turn.get('sources', [])
                    break
            answer = IntelligenceHandler.format_sources_response(recent_sources)
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer)
            return ResponseFormatter.format_response(
                answer=answer,
                intent_label='System Info',
                intent_category='System Info',
                confidence=1.0,
                context=recent_sources,
            )

        if IntelligenceHandler.detect_out_of_scope(query):
            answer = IntelligenceHandler.get_out_of_scope_response()
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer)
            return ResponseFormatter.format_response(
                answer=answer,
                intent_label='Out of Scope',
                intent_category='Out of Scope',
                confidence=1.0,
                context=[],
            )

        # Check for greeting or casual conversation
        greeting_response = self.greeting_handler.get_greeting_response(query)
        if greeting_response:
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', greeting_response['answer'])
            return greeting_response

        # Try improved keyword-based intent classification first
        keyword_result = self.improved_classifier.classify_by_keywords(query)
        intent_label = None
        confidence = None

        if keyword_result:
            intent_label, confidence = keyword_result
        else:
            # Fallback to existing retrieval classifier
            intent = self.classifier.classify(query)
            intent_label = str(intent['intent_label'])
            confidence = float(intent['confidence'])

        # Get display name for intent
        display_name = self.improved_classifier.get_display_name(intent_label)

        # Retrieve context from FAISS
        retrieved = retrieve(str(query), top_k=self.top_k)
        context_rows = []
        for _, row in retrieved.iterrows():
            context_rows.append({
                'conversation_id': row.get('conversation_id', ''),
                'customer_query': row.get('customer_query', ''),
                'amazon_response': row.get('amazon_response', ''),
                'intent_label': row.get('intent_label', intent_label),
                'similarity_score': float(row.get('similarity_score', 0.0)),
            })

        # Build response using template
        base_answer = self._grounded_answer(query, context_rows)

        # Apply response template for better structure
        answer = ResponseTemplateBuilder.build_response(
            intent=display_name,
            base_answer=base_answer,
            context=context_rows,
        )

        # Add low confidence disclaimer if needed
        if confidence < 0.4:
            answer = self.improved_classifier.get_low_confidence_message(answer)

        self.memory.add_turn('user', query)
        self.memory.add_turn('assistant', answer)

        return ResponseFormatter.format_response(
            answer=answer,
            intent_label=display_name,
            intent_category=display_name,
            confidence=float(confidence),
            context=context_rows,
        )

