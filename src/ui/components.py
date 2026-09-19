from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import streamlit as st


# Intent display labels mapping (production-friendly names)
INTENT_DISPLAY_NAMES = {
    "orders": "Orders",
    "order": "Orders",
    "returns": "Returns & Refunds",
    "return": "Returns & Refunds",
    "refunds": "Returns & Refunds",
    "refund": "Returns & Refunds",
    "prime": "Prime Membership",
    "membership": "Prime Membership",
    "promotions": "Promotions & Coupons",
    "coupons": "Promotions & Coupons",
    "delivery": "Delivery",
    "shipping": "Delivery",
    "login": "Login & Authentication",
    "auth": "Login & Authentication",
    "technical": "Technical Issue",
    "issue": "Technical Issue",
    "other": "Other Support",
}


def get_display_intent(intent: str | None) -> str:
    """Convert intent label to production display name."""
    if not intent:
        return "Other Support"
    normalized = intent.lower().strip()
    return INTENT_DISPLAY_NAMES.get(normalized, intent or "Other Support")


def system_status_card() -> None:
    """Render production AI assistant status card."""
    st.markdown(
        """
        <div class="status-card">
            <div class="status-header">Production AI Assistant</div>
            <div class="status-item">
                <span class="dot"></span>
                System Status
                <span class="status-badge">Active</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def api_status_display(is_online: bool) -> None:
    """Render API status with badge."""
    status_class = "" if is_online else "offline"
    status_text = "Online" if is_online else "Offline"
    st.markdown(
        f"""
        <div class="status-item">
            <span class="dot {status_class}"></span>
            API Status
            <span class="status-badge {status_class}">{status_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def retriever_status_display() -> None:
    """Render retriever status."""
    st.markdown(
        """
        <div class="status-item">
            <span class="dot"></span>
            Retriever Status
            <span class="status-badge">Loaded</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def embedding_model_display() -> None:
    """Render embedding model info."""
    st.markdown(
        """
        <div class="status-item">
            Embedding Model
            <span class="status-badge">MiniLM-L6-v2</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def knowledge_base_display() -> None:
    """Render knowledge base info."""
    st.markdown(
        """
        <div class="status-item">
            Knowledge Base
            <span class="status-badge">10,000 Conversations</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def intent_badge(intent: str | None) -> None:
    """Render professional intent badge."""
    display_intent = get_display_intent(intent)
    st.markdown(
        f'<span class="intent-badge">📋 Intent: {display_intent}</span>',
        unsafe_allow_html=True,
    )


def confidence_meter(confidence: float | None) -> None:
    """Render confidence meter with bar."""
    score = float(confidence or 0.0)
    score = max(0.0, min(score, 1.0))
    st.markdown(
        f"""
        <div class="metric-box">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <strong>Confidence</strong>
                <span>{score:.0%}</span>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width:{score*100:.0f}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_bubble(role: str, content: str, timestamp: str | None = None) -> None:
    """Render chat bubble with timestamp."""
    message_class = "chat-message-user" if role == "user" else "chat-message-assistant"
    ts = timestamp or datetime.utcnow().strftime("%H:%M")
    role_icon = "👤" if role == "user" else "🤖"
    role_label = "You" if role == "user" else "Assistant"

    st.markdown(
        f"""
        <div class="{message_class}">
            <div style="font-size:0.8rem; opacity:0.7; margin-bottom:0.5rem; font-weight:500;">{role_icon} {role_label} · {ts}</div>
            <div style="line-height:1.5;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_card(source: dict[str, Any]) -> None:
    """Render source card with professional styling."""
    conversation_id = source.get("conversation_id") or source.get("source") or "Knowledge Base Reference"
    similarity = source.get("similarity_score") or source.get("score") or 0.0

    st.markdown(
        f"""
        <div class="source-card">
            <div style="font-weight:600; margin-bottom:0.35rem; font-size:0.9rem;">📚 {conversation_id}</div>
            <div style="font-size:0.8rem; opacity:0.8;">Match: {float(similarity):.1%}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: Iterable[dict[str, Any]]) -> None:
    """Render all retrieved sources."""
    items = list(sources or [])
    if not items:
        st.caption("No retrieved sources for this query.")
        return

    st.subheader("Retrieved Sources", divider=False)
    for item in items:
        render_source_card(item)

