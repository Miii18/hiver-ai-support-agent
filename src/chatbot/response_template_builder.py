from __future__ import annotations

from typing import Any


class ResponseTemplateBuilder:
    """Build context-aware response templates based on intent."""

    INTENT_TEMPLATES = {
        "Returns & Refunds": {
            "intro": "Regarding your refund or return request:",
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
            "intro": "Regarding your delivery concern:",
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
            "intro": "Regarding your order:",
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
            "intro": "Regarding your Prime membership:",
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
            "intro": "Regarding your login or account access issue:",
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
            "intro": "Regarding promo codes or coupons:",
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
            "intro": "Regarding a technical issue:",
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

        # Build response from template
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
