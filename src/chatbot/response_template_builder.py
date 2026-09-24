from __future__ import annotations

from typing import Any


class ResponseTemplateBuilder:
    """Build context-aware response templates based on intent."""

    INTENT_TEMPLATES = {
        "Returns & Refunds": {
            "intro": "It looks like you want to return or refund an item.",
            "details": [
                "Check your refund status in your account under 'Returns'",
                "Returns typically take 5-7 business days to process",
                "Once approved, refunds appear within 3-5 business days",
            ],
            "actions": [
                "You can initiate a return directly from your order details",
                "Select a reason for the return and print the label",
                "Drop off the item at an Amazon return location",
            ],
            "escalation": "If your refund isn't processed within the expected timeframe, contact support.",
        },
        "Delivery": {
            "intro": "It looks like you're experiencing a delivery issue.",
            "details": [
                "You can track your package in real-time with the tracking number",
                "Most deliveries arrive within the estimated date range",
                "Late deliveries may qualify for compensation",
            ],
            "actions": [
                "Check your order for the tracking number and carrier",
                "Visit the carrier's website or use Amazon's tracking",
                "Contact the carrier if delivery is significantly delayed",
            ],
            "escalation": "If your package doesn't arrive by the promised date, we can help.",
        },
        "Orders": {
            "intro": "Here's guidance for your Amazon order.",
            "details": [
                "You can check your order status in 'Your Orders'",
                "Processing typically takes 1-2 hours after placement",
                "Shipping estimates are shown during checkout",
            ],
            "actions": [
                "Review order details and payment information",
                "Check the estimated delivery date",
                "Update delivery address before shipment",
            ],
            "escalation": "Contact support if you need to modify or cancel your order urgently.",
        },
        "Prime Membership": {
            "intro": "Here's guidance for your Prime membership.",
            "details": [
                "Prime membership costs $14.99/month or $139/year",
                "You get free 2-day shipping, Prime Video, and more",
                "You can cancel anytime from your account settings",
            ],
            "actions": [
                "Manage your membership in Account > Prime membership",
                "Renew or cancel directly without calling support",
                "View all Prime member benefits on your account",
            ],
            "escalation": "If you have billing questions, we can help clarify.",
        },
        "Login & Authentication": {
            "intro": "Let's help you recover your Amazon account.",
            "details": [
                "Password resets are instant and sent to your email",
                "Two-factor authentication provides extra security",
                "Account lockouts are temporary for security",
            ],
            "actions": [
                "Use 'Forgot Password' to reset your password",
                "Check your email for the reset link (valid for 24 hours)",
                "Enable 2FA in Account > Login & security for protection",
            ],
            "escalation": "If you don't receive the reset email, check spam folder or contact support.",
        },
        "Promotions & Coupons": {
            "intro": "Let's troubleshoot your coupon or promotional offer.",
            "details": [
                "Coupons must be applied at checkout before purchase",
                "Some coupons are category-specific and have restrictions",
                "Invalid coupons may be expired or not applicable",
            ],
            "actions": [
                "Check coupon terms for restrictions and expiration",
                "Ensure the coupon applies to items in your cart",
                "Try clearing cache if the code still doesn't work",
            ],
            "escalation": "Contact support if you believe the code should work.",
        },
        "Technical Issue": {
            "intro": "It looks like you're experiencing a technical issue.",
            "details": [
                "Try clearing browser cache and cookies first",
                "Update to the latest version of the app",
                "Try a different browser or device to isolate the issue",
            ],
            "actions": [
                "Restart the app or browser completely",
                "Check your internet connection stability",
                "Disable browser extensions that might interfere",
            ],
            "escalation": "If the issue persists, please describe the exact error message you see.",
        },
    }

    # Maps escalation intent categories to specific guidance templates
    ESCALATION_TEMPLATES = {
        "security": {
            "title": "Account Security Escalation",
            "steps": [
                "Immediately change your Amazon password via 'Forgot Password'",
                "Go to Account > Login & security and review recent activity",
                "Enable Two-Factor Authentication (2FA) for extra protection",
                "Check for any unrecognized orders in 'Your Orders' and report them",
                "If your email was compromised, recover it first then reset Amazon password",
            ],
            "note": "A specialist will verify your identity and secure your account.",
        },
        "billing": {
            "title": "Billing & Payment Investigation",
            "steps": [
                "A payment specialist will review your billing history",
                "Have your last 4 card digits and billing date ready",
                "Check your bank statement for the transaction reference number",
                "If the charge is unrecognized, request a temporary hold via your bank",
                "Our team will contact you within 1-2 business days with findings",
            ],
            "note": "Please do not dispute the charge with your bank until our team investigates.",
        },
        "fraud": {
            "title": "Unauthorized Purchase Investigation",
            "steps": [
                "Do not cancel or return any unauthorized orders yet — preserve evidence",
                "Screenshot any orders you did not place in 'Your Orders'",
                "A fraud specialist will review your account and unauthorized transactions",
                "You will not be held liable for confirmed unauthorized charges",
                "Expect a follow-up within 24 hours with next steps",
            ],
            "note": "Your account has been flagged for priority fraud review.",
        },
        "refund": {
            "title": "Refund Investigation",
            "steps": [
                "A refund specialist will review your case for expedited processing",
                "Have your order number and original payment method ready",
                "Refunds under investigation are typically resolved within 3-5 business days",
                "You will receive an email confirmation once the refund is approved",
                "If the item was returned, confirm your tracking shows delivery to our warehouse",
            ],
            "note": "Our team will prioritize your refund and keep you updated.",
        },
    }

    # Maps intent labels to escalation categories
    _INTENT_TO_ESCALATION_CATEGORY = {
        "login & authentication": "security",
        "login and authentication": "security",
        "security": "security",
        "billing": "billing",
        "prime membership": "billing",
        "fraud": "fraud",
        "returns & refunds": "refund",
        "returns and refunds": "refund",
        "refund": "refund",
    }

    # Banner config keyed by escalation_type
    BANNER_CONFIG = {
        "security": {
            "color": "#dc2626",
            "border": "#991b1b",
            "bg_gradient": "linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%)",
            "badge_bg": "#dc2626",
            "icon": "🔴",
            "label": "Escalation Required — Account Security",
            "friendly_reason": "Possible account compromise detected.",
            "next_steps": [
                "Reset your password immediately.",
                "Enable two-factor authentication.",
                "Review recent login activity.",
                "A human support specialist has been notified.",
            ],
        },
        "billing": {
            "color": "#ea580c",
            "border": "#9a3412",
            "bg_gradient": "linear-gradient(135deg, #431407 0%, #7c2d12 100%)",
            "badge_bg": "#ea580c",
            "icon": "🟠",
            "label": "Escalation Required — Billing Investigation",
            "friendly_reason": "A duplicate charge was detected.",
            "next_steps": [
                "Review recent transactions.",
                "Verify payment method.",
                "Billing specialist notified.",
                "Investigation has started.",
            ],
        },
        "refund": {
            "color": "#2563eb",
            "border": "#1e3a8a",
            "bg_gradient": "linear-gradient(135deg, #172554 0%, #1e3a8a 100%)",
            "badge_bg": "#2563eb",
            "icon": "🔵",
            "label": "Refund Investigation",
            "friendly_reason": "Refund investigation required.",
            "next_steps": [
                "A refund specialist will prioritize your case immediately.",
                "Have your order number and original payment method ready.",
                "Confirm your return tracking shows delivery to our warehouse.",
                "You will receive an email update within 3–5 business days.",
            ],
        },
        "damaged": {
            "color": "#d97706",
            "border": "#92400e",
            "bg_gradient": "linear-gradient(135deg, #451a03 0%, #78350f 100%)",
            "badge_bg": "#d97706",
            "icon": "🟡",
            "label": "Damaged Item Report",
            "friendly_reason": "Your package appears damaged during delivery.",
            "next_steps": [
                "Upload photos of the damaged package.",
                "Start a replacement or return request.",
                "Returns specialist notified.",
            ],
        },
        "general": {
            "color": "#7c3aed",
            "border": "#4c1d95",
            "bg_gradient": "linear-gradient(135deg, #2e1065 0%, #4c1d95 100%)",
            "badge_bg": "#7c3aed",
            "icon": "🟣",
            "label": "Escalated to Support",
            "friendly_reason": "This issue has been escalated for human review.",
            "next_steps": [
                "A human support specialist has been assigned to your case.",
                "Please have your order or account details ready.",
                "You will be contacted within 1–2 business days.",
                "Reference this conversation for faster resolution.",
            ],
        },
    }

    # Query-level pattern → (escalation_type, friendly_reason)
    _QUERY_PATTERN_MAP: list[tuple[str, str, str]] = [
        # security
        (r"hack|compromise|breach|unauthori[sz]ed.*access|someone.*log|account.*stolen", "security", "Possible account compromise detected."),
        (r"fraud|scam|stolen|chargeback|dispute.*charge|unauthorized.*charge|charge.*unauthorized", "billing", "A duplicate charge was detected."),
        # billing / duplicate charge
        (r"charge.*twice|double.*charge|charged.*twice|duplicate.*charge|bill.*twice", "billing", "A duplicate charge was detected."),
        (r"charge.*wrong|wrong.*amount|overcharg|incorrect.*bill|incorrect.*charge", "billing", "A duplicate charge was detected."),
        # refund
        (r"refund.*pending|pending.*refund|refund.*long|refund.*waiting|refund.*month|refund.*week|refund.*45|refund.*30", "refund", "Refund investigation required."),
        (r"refund.*not.*receiv|haven.*receiv.*refund|where.*refund|no.*refund", "refund", "Refund investigation required."),
        # damaged / torn / broken item (not wrong item — wrong item is a return/exchange, not damage)
        (r"torn|ripped|damaged|broken|crushed|dent|scratch|defect|poor.*condition|bad.*condition|ruined", "damaged", "Your package appears damaged during delivery."),
        # legal / threat
        (r"legal|lawsuit|lawyer|attorney|sue|threat", "security", "Possible account compromise detected."),
        (r"emergency", "general", "Emergency situation reported."),
    ]

    @classmethod
    def _get_escalation_category(cls, intent: str) -> str:
        """Map an intent label to an escalation template category."""
        key = intent.lower().strip()
        return cls._INTENT_TO_ESCALATION_CATEGORY.get(key, "")

    @classmethod
    def classify_escalation_type(
        cls,
        query: str,
        intent: str,
        raw_reason: str,
    ) -> tuple[str, str]:
        """Return (escalation_type, human_friendly_reason) from query text and intent."""
        import re
        q = query.lower()

        for pattern, esc_type, friendly in cls._QUERY_PATTERN_MAP:
            if re.search(pattern, q):
                return esc_type, friendly

        # Fall back to intent mapping
        category = cls._get_escalation_category(intent)
        if category in cls.BANNER_CONFIG:
            intent_friendly = {
                "security": "Possible account security issue detected.",
                "billing": "Billing issue requires specialist review.",
                "fraud": "Possible fraudulent activity detected.",
                "refund": "Refund investigation required.",
                "damaged": "Damaged or incorrect item reported.",
            }
            return category, intent_friendly.get(category, "Issue escalated for human review.")

        return "general", "This issue has been escalated for human review."

    @classmethod
    def build_escalation_response(
        cls,
        intent: str,
        base_answer: str,
        escalation_reason: str,
    ) -> str:
        """Build an intent-specific escalation response."""
        category = cls._get_escalation_category(intent)
        template = cls.ESCALATION_TEMPLATES.get(category)

        if not template:
            # Generic fallback — never use Delivery template for escalated queries
            return (
                f"{base_answer}\n\n"
                "**A human support specialist has been alerted** and will follow up with you shortly.\n\n"
                f"**Issue flagged:** {escalation_reason}"
            )

        parts = [
            f"**{template['title']}**",
            "",
            base_answer,
            "",
            "**Immediate steps taken / what to do now:**",
        ]
        for step in template["steps"]:
            parts.append(f"• {step}")
        parts.extend([
            "",
            f"**Note:** {template['note']}",
        ])
        return "\n".join(parts)

    @classmethod
    def build_response(
        cls,
        intent: str,
        base_answer: str,
        context: list[dict[str, Any]],
    ) -> str:
        """Build a full response using template structure."""
        template = cls.INTENT_TEMPLATES.get(intent)

        if not template:
            return base_answer

        response_parts = [
            template["intro"],
            "",
            base_answer,
            "",
            "**What you should know:**",
        ]

        for detail in template["details"]:
            response_parts.append(f"• {detail}")

        response_parts.extend([
            "",
            "**What you can do:**",
        ])

        for action in template["actions"]:
            response_parts.append(f"• {action}")

        response_parts.extend([
            "",
            f"**Need more help?** {template['escalation']}",
        ])

        if context:
            response_parts.extend([
                "",
                "**Based on similar cases in our knowledge base:**",
            ])
            for idx, source in enumerate(context[:2], 1):
                similarity = source.get("similarity_score", 0.0)
                response_parts.append(f"  {idx}. Match {similarity:.0%} - {source.get('conversation_id', 'Reference')}")

        return "\n".join(response_parts)

    @classmethod
    def get_low_confidence_disclaimer(cls, base_answer: str, confidence: float) -> str:
        """Return response with low confidence disclaimer."""
        return (
            f"I found the closest available customer support guidance, but my confidence is only {confidence:.0%}. "
            f"Please verify this matches your concern:\n\n{base_answer}"
        )
