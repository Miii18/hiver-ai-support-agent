from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import streamlit as st


def status_pill(label: str, is_ok: bool = True) -> None:
    color = "#2ecc71" if is_ok else "#e74c3c"
    st.markdown(
        f'<span class="status-pill" style="border-color:{color}; color:{color}; background:rgba(255,255,255,0.04);">{label}</span>',
        unsafe_allow_html=True,
    )


def intent_badge(intent: str | None) -> None:
    label = intent or "General"
    st.markdown(f'<span class="status-pill">Intent: {label}</span>', unsafe_allow_html=True)


def confidence_meter(confidence: float | None) -> None:
    score = float(confidence or 0.0)
    score = max(0.0, min(score, 1.0))
    st.markdown(
        f"""
        <div class="metric-box">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.35rem;">
                <strong>Confidence</strong>
                <span>{score:.0%}</span>
            </div>
            <div style="height:10px; background: rgba(255,255,255,0.08); border-radius:999px; overflow:hidden;">
                <div style="height:100%; width:{score*100:.0f}%; background: linear-gradient(90deg, #ff9900, #f7b267); border-radius:999px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_bubble(role: str, content: str, timestamp: str | None = None) -> None:
    message_class = "chat-message-user" if role == "user" else "chat-message-assistant"
    ts = timestamp or datetime.utcnow().strftime("%H:%M")
    st.markdown(
        f"""
        <div class="{message_class}">
            <div style="font-size:0.72rem; opacity:0.75; margin-bottom:0.45rem;">{role.upper()} · {ts}</div>
            <div>{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_card(source: dict[str, Any]) -> None:
    conversation_id = source.get("conversation_id") or source.get("source") or "Unknown source"
    similarity = source.get("similarity_score") or source.get("score") or 0.0
    st.markdown(
        f"""
        <div class="source-card">
            <div style="font-weight:700; margin-bottom:0.25rem;">{conversation_id}</div>
            <div style="font-size:0.75rem; opacity:0.8;">Similarity: {float(similarity):.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: Iterable[dict[str, Any]]) -> None:
    items = list(sources or [])
    if not items:
        st.caption("No retrieved sources this turn.")
        return
    st.subheader("Retrieved sources")
    for item in items:
        render_source_card(item)
