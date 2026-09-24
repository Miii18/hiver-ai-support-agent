from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import streamlit as st


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
    if not intent:
        return "Other Support"
    normalized = intent.lower().strip()
    return INTENT_DISPLAY_NAMES.get(normalized, intent or "Other Support")


def system_status_card() -> None:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-header">Production AI Assistant</div>
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
                <span class="status-pill pill-green">🟢 API Online</span>
                <span class="status-pill pill-green">🟢 FAISS Loaded</span>
                <span class="status-pill pill-green">🟢 Knowledge Base</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def api_status_display(is_online: bool) -> None:
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
    st.markdown(
        """
        <div class="status-item">
            <span class="dot"></span>
            FAISS Retriever
            <span class="status-badge">Loaded</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def embedding_model_display() -> None:
    st.markdown(
        """
        <div class="status-item">
            <span style="width:7px;height:7px;background:#3b82f6;border-radius:50%;display:inline-block;flex-shrink:0;"></span>
            Embedding Model
            <span class="status-badge">MiniLM-L6-v2</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def knowledge_base_display() -> None:
    st.markdown(
        """
        <div class="status-item">
            <span style="width:7px;height:7px;background:#3b82f6;border-radius:50%;display:inline-block;flex-shrink:0;"></span>
            Knowledge Base
            <span class="status-badge">10,000 Cases</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def intent_badge(intent: str | None) -> None:
    display_intent = get_display_intent(intent)
    st.markdown(
        f'<span class="intent-chip">📋 {display_intent}</span>',
        unsafe_allow_html=True,
    )


def confidence_meter(confidence: float | None) -> None:
    score = float(confidence or 0.0)
    score = max(0.0, min(score, 1.0))
    pct = score * 100

    if score >= 0.7:
        badge_class, bar_class, label = "conf-high", "conf-bar-high", "High"
    elif score >= 0.4:
        badge_class, bar_class, label = "conf-med", "conf-bar-med", "Medium"
    else:
        badge_class, bar_class, label = "conf-low", "conf-bar-low", "Low"

    st.markdown(
        f"""
        <div class="confidence-wrap">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.45rem;">
                <span style="font-size:0.82rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;">Confidence</span>
                <span class="conf-badge {badge_class}">{pct:.0f}% — {label}</span>
            </div>
            <div class="conf-bar-track">
                <div class="conf-bar-fill {bar_class}" style="width:{pct:.1f}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_bubble(role: str, content: str, timestamp: str | None = None) -> None:
    ts = timestamp or datetime.utcnow().strftime("%I:%M %p")
    if role == "user":
        st.markdown(
            f"""<div class="chat-row-user">
<div class="chat-bubble-wrapper" style="align-items:flex-end;">
<div class="chat-bubble-user">{content}</div>
<div class="bubble-meta" style="text-align:right;">{ts}</div>
</div>
<div class="chat-avatar">👤</div>
</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div class="chat-row-assistant">
<div class="chat-avatar">🤖</div>
<div class="chat-bubble-wrapper" style="align-items:flex-start;">
<div class="chat-bubble-assistant">{content}</div>
<div class="bubble-meta">{ts}</div>
</div>
</div>""",
            unsafe_allow_html=True,
        )


def render_source_card(source: dict[str, Any]) -> None:
    conversation_id = source.get("conversation_id") or source.get("source") or "Knowledge Base Reference"
    similarity = float(source.get("similarity_score") or source.get("score") or 0.0)

    if similarity >= 0.7:
        rel_class, rel_label = "rel-high", "High"
    elif similarity >= 0.4:
        rel_class, rel_label = "rel-med", "Medium"
    else:
        rel_class, rel_label = "rel-low", "Low"

    st.markdown(
        f"""
        <div class="source-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                <span style="font-weight:600;font-size:0.88rem;">📚 {conversation_id}</span>
                <span class="relevance-badge {rel_class}">{rel_label} Match</span>
            </div>
            <div style="font-size:0.78rem;color:var(--muted);">Similarity: {similarity:.1%}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: Iterable[dict[str, Any]]) -> None:
    items = list(sources or [])
    if not items:
        st.caption("No retrieved sources for this query.")
        return

    st.markdown(
        '<div class="sources-header">🔍 Retrieved Sources</div>',
        unsafe_allow_html=True,
    )
    for item in items:
        render_source_card(item)
