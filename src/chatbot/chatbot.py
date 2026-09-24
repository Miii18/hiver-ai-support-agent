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
from src.escalation.escalation_engine import EscalationEngine
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
        self.escalation_engine = EscalationEngine()

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
            # Get most recent sources from memory (stored on assistant turns)
            recent_sources = self.memory.previous_sources
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
        elif self.memory.active_intent:
            # Carry over previous intent for vague follow-up queries
            intent_label = self.memory.active_intent
            confidence = 0.85
        else:
            # Fallback to existing retrieval classifier
            intent = self.classifier.classify(query)
            intent_label = str(intent['intent_label'])
            confidence = float(intent['confidence'])

        # Persist active intent for follow-ups
        self.memory.active_intent = intent_label

        # Run escalation check BEFORE FAISS retrieval
        escalation = self.escalation_engine.decide(
            query=query,
            intent=intent_label,
            confidence=float(confidence),
            context=[],
        )
        escalation_triggered = escalation.get('escalation_decision') == 'ESCALATE_TO_HUMAN'

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

        # Delivery compensation follow-up: active Delivery intent + compensation query
        _compensation_terms = {
            "compensation", "compensate", "compensated", "shipping credit", "credit",
            "reimburse", "reimbursement", "late delivery", "delivery late", "refund for delay",
            "delayed delivery",
        }
        _active_is_delivery = (self.memory.active_intent or "").lower() == "delivery"
        _query_lower = query.lower()
        _is_compensation_query = any(term in _query_lower for term in _compensation_terms)

        if _active_is_delivery and _is_compensation_query and not escalation_triggered:
            answer = (
                "**Delivery Compensation — What You're Entitled To**\n\n"
                "If your delivery was late or failed to arrive on time, Amazon may offer the following:\n\n"
                "**What you should know:**\n"
                "• Late deliveries may qualify for a shipping fee refund (if you paid for expedited shipping)\n"
                "• Amazon may issue a promotional credit as a goodwill gesture for significant delays\n"
                "• If the package is lost, a full replacement or refund is available\n"
                "• Prime members may receive extended benefits for repeated late deliveries\n\n"
                "**What you can do:**\n"
                "• Go to Your Orders → select the order → 'Problem with order' → report late delivery\n"
                "• Chat with Amazon support and reference the promised delivery date\n"
                "• Request a shipping credit or promotional credit directly in the chat\n"
                "• If the item never arrived, initiate a 'Where's My Package' investigation\n\n"
                "**Need more help?** If compensation is not offered automatically, a support specialist can escalate your case for a manual review."
            )
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer, sources=context_rows)
            result = ResponseFormatter.format_response(
                answer=answer,
                intent_label=display_name,
                intent_category=display_name,
                confidence=float(confidence),
                context=context_rows,
            )
            result['escalation'] = escalation
            result['escalation_triggered'] = False
            return result

        # --- Query-level response overrides (Bug fixes) ---
        _q = query.lower()

        # Bug 1: Wrong item ordered → Return / Exchange Request template
        _wrong_item_terms = {"wrong item", "incorrect product", "incorrect item", "ordered wrong", "wrong product delivered"}
        if any(t in _q for t in _wrong_item_terms):
            answer = (
                "**Return / Exchange Request — Wrong Item Received**\n\n"
                "We're sorry you received the wrong item. Here's how to resolve it:\n\n"
                "**What you should know:**\n"
                "• Wrong item deliveries are eligible for a free return and re-shipment\n"
                "• You won't be charged for return shipping in this case\n"
                "• A replacement or full refund can be requested within 30 days of delivery\n\n"
                "**What you can do:**\n"
                "• Go to **Your Orders** → select the order → **'Problem with order'**\n"
                "• Choose **'Wrong item was sent'** as the reason\n"
                "• Select **Return for Refund** or **Send me the right one** (replacement)\n"
                "• Print the prepaid return label and drop it off at any return location\n\n"
                "**Need more help?** If no replacement is available, a full refund will be issued within 3–5 business days."
            )
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer, sources=context_rows)
            result = ResponseFormatter.format_response(
                answer=answer,
                intent_label=display_name,
                intent_category=display_name,
                confidence=float(confidence),
                context=context_rows,
            )
            result['escalation'] = escalation
            result['escalation_triggered'] = False
            return result

        # Bug 2: Update delivery address → address update steps
        _address_terms = {"update delivery address", "change shipping address", "change address", "update address", "shipping address"}
        if any(t in _q for t in _address_terms):
            answer = (
                "**Update Delivery Address**\n\n"
                "You may be able to update your delivery address before the order ships:\n\n"
                "**What you should know:**\n"
                "• Address changes are only possible before the order enters the shipping phase\n"
                "• Once the carrier has collected the package, the address cannot be changed\n"
                "• For urgent changes, contact support immediately after placing the order\n\n"
                "**What you can do:**\n"
                "• Go to **Your Orders** → find the order → click **'Change delivery address'** (if available)\n"
                "• If the option is greyed out, the order has already been dispatched\n"
                "• For dispatched orders, contact the carrier directly using the tracking number\n"
                "• As a last resort, you can refuse delivery and request a reship to the correct address\n\n"
                "**Need more help?** Contact support as early as possible — address updates have a narrow time window."
            )
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer, sources=context_rows)
            result = ResponseFormatter.format_response(
                answer=answer,
                intent_label=display_name,
                intent_category=display_name,
                confidence=float(confidence),
                context=context_rows,
            )
            result['escalation'] = escalation
            result['escalation_triggered'] = False
            return result

        # Bug 3: Exchange requests → dedicated Exchange Response
        _exchange_terms = {"exchange my", "exchange this", "replace with another", "exchange product", "swap for another"}
        if any(t in _q for t in _exchange_terms):
            answer = (
                "**Exchange Request**\n\n"
                "We can help you exchange your item for a different size, colour, or model:\n\n"
                "**What you should know:**\n"
                "• Exchanges are available for eligible items within 30 days of delivery\n"
                "• The item must be unused, in original packaging, and in resalable condition\n"
                "• If the exact variant is out of stock, a full refund will be offered instead\n\n"
                "**What you can do:**\n"
                "• Go to **Your Orders** → select the item → **'Return or Replace Items'**\n"
                "• Choose **'Replace'** and select the new size or variant you want\n"
                "• Print the return label and ship back the original item\n"
                "• Your replacement will be dispatched once the return is received\n\n"
                "**Need more help?** If the exchange option is not available online, a support agent can process it manually."
            )
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer, sources=context_rows)
            result = ResponseFormatter.format_response(
                answer=answer,
                intent_label=display_name,
                intent_category=display_name,
                confidence=float(confidence),
                context=context_rows,
            )
            result['escalation'] = escalation
            result['escalation_triggered'] = False
            return result

        # Bug 4: Checkout errors → Technical Support troubleshooting
        _checkout_terms = {"checkout", "payment page", "unable to place order", "checkout failed", "checkout error"}
        if any(t in _q for t in _checkout_terms):
            answer = (
                "**Checkout / Payment Error Troubleshooting**\n\n"
                "We're sorry you're having trouble completing your order. Here's how to fix it:\n\n"
                "**What you should know:**\n"
                "• Checkout errors are often caused by browser cache, expired sessions, or payment method issues\n"
                "• Your card may have been temporarily blocked by your bank as a fraud precaution\n"
                "• Multiple failed attempts can temporarily lock checkout — wait 15 minutes before retrying\n\n"
                "**What you can do:**\n"
                "• Clear your browser cache and cookies, then reload the page\n"
                "• Try a different browser (Chrome, Firefox, Safari) or the Amazon mobile app\n"
                "• Verify your payment method is valid and has sufficient funds\n"
                "• Remove and re-add your payment method in **Account → Payment options**\n"
                "• Disable browser extensions (especially ad-blockers) that may interfere with checkout\n\n"
                "**Need more help?** If the error persists, note the exact error message and contact support with your cart details."
            )
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer, sources=context_rows)
            result = ResponseFormatter.format_response(
                answer=answer,
                intent_label=display_name,
                intent_category=display_name,
                confidence=float(confidence),
                context=context_rows,
            )
            result['escalation'] = escalation
            result['escalation_triggered'] = False
            return result

        # Bug 5: Delivery agent contact → tracking-based contact info
        _delivery_agent_terms = {"delivery agent", "delivery person", "delivery partner", "delivery man", "delivery woman"}
        if any(t in _q for t in _delivery_agent_terms):
            answer = (
                "**Contacting Your Delivery Partner**\n\n"
                "Direct contact with delivery agents depends on the carrier assigned to your order:\n\n"
                "**What you should know:**\n"
                "• Amazon Logistics deliveries may include a one-time delivery notification with a contact option\n"
                "• Third-party carriers (UPS, FedEx, USPS) have their own customer service lines\n"
                "• Phone numbers for individual delivery agents are generally not shared for privacy reasons\n\n"
                "**What you can do:**\n"
                "• Open your order in **Your Orders** and click **'Track Package'**\n"
                "• On the tracking page, check for a **'Contact carrier'** or **'Leave delivery instructions'** option\n"
                "• For Amazon Logistics, you may receive an SMS with a one-time agent contact link\n"
                "• Contact the carrier's customer service using the tracking number for delivery updates\n\n"
                "**Need more help?** If you need to leave special delivery instructions, add them on the tracking page before the delivery attempt."
            )
            self.memory.add_turn('user', query)
            self.memory.add_turn('assistant', answer, sources=context_rows)
            result = ResponseFormatter.format_response(
                answer=answer,
                intent_label=display_name,
                intent_category=display_name,
                confidence=float(confidence),
                context=context_rows,
            )
            result['escalation'] = escalation
            result['escalation_triggered'] = False
            return result

        # Apply response template for better structure
        if escalation_triggered:
            escalation_intent = escalation.get('escalation_intent', display_name)
            escalation_reason = escalation.get('escalation_reason', 'This query requires human review.')
            answer = ResponseTemplateBuilder.build_escalation_response(
                intent=escalation_intent,
                base_answer=base_answer,
                escalation_reason=escalation_reason,
            )
        else:
            answer = ResponseTemplateBuilder.build_response(
                intent=display_name,
                base_answer=base_answer,
                context=context_rows,
            )

        # Add low confidence disclaimer if needed
        if confidence < 0.4:
            answer = self.improved_classifier.get_low_confidence_message(answer)

        self.memory.add_turn('user', query)
        # Store sources on the assistant turn so "show retrieved sources" can access them
        self.memory.add_turn('assistant', answer, sources=context_rows)

        result = ResponseFormatter.format_response(
            answer=answer,
            intent_label=display_name,
            intent_category=display_name,
            confidence=float(confidence),
            context=context_rows,
        )
        result['escalation'] = escalation
        result['escalation_triggered'] = escalation_triggered
        return result


