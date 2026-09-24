from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
import pytz

import streamlit as st

from src.ui.api_client import chat, health_check, reset_memory
from src.chatbot.response_template_builder import ResponseTemplateBuilder
from src.ui.components import (
    api_status_display,
    confidence_meter,
    embedding_model_display,
    intent_badge,
    knowledge_base_display,
    render_chat_bubble,
    render_sources,
    retriever_status_display,
    system_status_card,
)
from src.ui.theme import apply_theme


st.set_page_config(
    page_title="AI Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_local_time_format() -> str:
    """Get current time in user's local timezone, formatted as 12-hour (HH:MM AM/PM)."""
    try:
        tz_name = st.context.timezone
    except (AttributeError, RuntimeError):
        tz_name = None

    if not tz_name:
        tz_name = "Asia/Kolkata"

    try:
        tz = pytz.timezone(tz_name)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.timezone("Asia/Kolkata")

    local_time = datetime.now(tz)
    return local_time.strftime("%I:%M %p")


def initialize_state() -> None:
    """Initialize session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi there! I'm your AI support assistant. Ask me about orders, returns, delivery, promotions, account issues, or anything else I can help with.",
                "timestamp": get_local_time_format(),
            }
        ]


def render_sidebar() -> None:
    """Render production sidebar with status indicators."""
    with st.sidebar:
        st.markdown("### AI Support Agent")
        st.markdown("Enterprise customer support powered by AI")

        st.markdown("---")

        system_status_card()

        st.markdown("---")

        st.markdown(
            '<div class="status-header">System Status</div>',
            unsafe_allow_html=True,
        )
        api_status_display(health_check())
        retriever_status_display()
        embedding_model_display()
        knowledge_base_display()

        st.markdown("---")

        st.markdown(
            '<div class="status-header">Support Categories</div>',
            unsafe_allow_html=True,
        )

        friendly_categories = [
            ("📦", "Orders"),
            ("🚚", "Delivery & Tracking"),
            ("↩️", "Returns & Refunds"),
            ("🔐", "Login & Account Security"),
            ("⭐", "Prime Membership"),
            ("🎁", "Promotions & Coupons"),
            ("🛠️", "Technical Support"),
            ("💬", "Other Support"),
        ]
        for icon, label in friendly_categories:
            st.markdown(
                f'<div class="sidebar-cat-item"><span>{icon}</span><span>{label}</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Chat", use_container_width=True):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "New conversation started. How can I help you today?",
                        "timestamp": get_local_time_format(),
                    }
                ]
                st.rerun()

        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Conversation cleared. Ask me anything.",
                        "timestamp": get_local_time_format(),
                    }
                ]
                st.rerun()

        if st.button("🧠 Reset Memory", use_container_width=True):
            reset_memory()
            st.info("Conversation memory cleared on server.", icon="OK")

        st.markdown("---")
        chat_log = "\n\n".join(
            f"{msg['role'].upper()} ({msg.get('timestamp', '')}):\n{msg['content']}"
            for msg in st.session_state.messages
        )
        st.download_button(
            label="📄 Export Conversation",
            data=chat_log,
            file_name="support_conversation.txt",
            mime="text/plain",
            use_container_width=True,
        )


def render_header() -> None:
    st.markdown(
        """
        <div class="header-banner">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
                <div>
                    <h1 style="margin:0;font-size:1.8rem;font-weight:800;letter-spacing:-0.5px;">AI Support Assistant</h1>
                    <p style="margin:0.4rem 0 0 0;opacity:0.85;font-size:0.95rem;">Intelligent customer support powered by retrieval-augmented generation</p>
                </div>
                <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
                    <span class="status-pill pill-green">🟢 API Online</span>
                    <span class="status-pill pill-green">🟢 FAISS Loaded</span>
                    <span class="status-pill pill-green">🟢 Knowledge Base</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_escalation_banner(message: dict) -> None:
    """Render a colored escalation banner above the assistant bubble."""
    esc_type = message.get("esc_type", "general")
    escalation_priority = message.get("escalation_priority", "HIGH")
    cfg = ResponseTemplateBuilder.BANNER_CONFIG.get(esc_type, ResponseTemplateBuilder.BANNER_CONFIG["general"])
    priority_label = (escalation_priority or "HIGH").capitalize()
    display_reason = cfg["friendly_reason"]
    steps_html = "".join(
        f'<li style="margin:4px 0;">{step}</li>'
        for step in cfg["next_steps"]
    )
    st.markdown(
        f"""
        <div style="
            background:{cfg['bg_gradient']};
            color:#fff;
            border-radius:12px;
            padding:20px 22px;
            margin:14px 0;
            border-left:6px solid {cfg['border']};
            box-shadow:0 4px 16px rgba(0,0,0,0.35);
        ">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <span style="font-size:28px;line-height:1;">{cfg['icon']}</span>
                <div>
                    <div style="font-size:18px;font-weight:700;letter-spacing:0.3px;">{cfg['label']}</div>
                    <span style="
                        background:{cfg['badge_bg']};
                        color:#fff;
                        font-size:11px;
                        font-weight:700;
                        padding:2px 9px;
                        border-radius:20px;
                        letter-spacing:0.8px;
                        text-transform:uppercase;
                    ">Priority: {priority_label}</span>
                </div>
            </div>
            <div style="margin-bottom:12px;font-size:14px;opacity:0.95;">
                <b>Reason:</b> {display_reason}
            </div>
            <div style="background:rgba(255,255,255,0.07);border-radius:8px;padding:12px 14px;">
                <div style="font-size:13px;font-weight:600;margin-bottom:6px;opacity:0.85;text-transform:uppercase;letter-spacing:0.5px;">Next Steps</div>
                <ul style="margin:0;padding-left:18px;font-size:13px;opacity:0.92;line-height:1.6;">
                    {steps_html}
                </ul>
            </div>
            <div style="font-size:12px;opacity:0.7;margin-top:10px;border-top:1px solid rgba(255,255,255,0.15);padding-top:8px;">
                This issue has been routed to a human support specialist.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _bubble_html(message: dict) -> str:
    """Build chat bubble HTML string for a single message."""
    role = message["role"]
    content = message["content"]
    ts = message.get("timestamp") or ""
    if role == "user":
        return (
            f'<div class="chat-row-user">'
            f'<div class="chat-bubble-wrapper" style="align-items:flex-end;">'
            f'<div class="chat-bubble-user">{content}</div>'
            f'<div class="bubble-meta" style="text-align:right;">{ts}</div>'
            f'</div>'
            f'<div class="chat-avatar">👤</div>'
            f'</div>'
        )
    return (
        f'<div class="chat-row-assistant">'
        f'<div class="chat-avatar">🤖</div>'
        f'<div class="chat-bubble-wrapper" style="align-items:flex-start;">'
        f'<div class="chat-bubble-assistant">{content}</div>'
        f'<div class="bubble-meta">{ts}</div>'
        f'</div>'
        f'</div>'
    )


def _escalation_banner_html(message: dict) -> str:
    """Build escalation banner HTML string for inline embedding."""
    esc_type = message.get("esc_type", "general")
    escalation_priority = message.get("escalation_priority", "HIGH")
    cfg = ResponseTemplateBuilder.BANNER_CONFIG.get(esc_type, ResponseTemplateBuilder.BANNER_CONFIG["general"])
    priority_label = (escalation_priority or "HIGH").capitalize()
    display_reason = cfg["friendly_reason"]
    steps_html = "".join(
        f'<li style="margin:4px 0;">{step}</li>'
        for step in cfg["next_steps"]
    )
    return (
        f'<div style="'
        f'background:{cfg["bg_gradient"]};'
        f'color:#fff;'
        f'border-radius:12px;'
        f'padding:20px 22px;'
        f'margin:14px 0;'
        f'border-left:6px solid {cfg["border"]};'
        f'box-shadow:0 4px 16px rgba(0,0,0,0.35);">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
        f'<span style="font-size:28px;line-height:1;">{cfg["icon"]}</span>'
        f'<div>'
        f'<div style="font-size:18px;font-weight:700;letter-spacing:0.3px;">{cfg["label"]}</div>'
        f'<span style="'
        f'background:{cfg["badge_bg"]};'
        f'color:#fff;font-size:11px;font-weight:700;'
        f'padding:2px 9px;border-radius:20px;'
        f'letter-spacing:0.8px;text-transform:uppercase;">'
        f'Priority: {priority_label}</span>'
        f'</div></div>'
        f'<div style="margin-bottom:12px;font-size:14px;opacity:0.95;">'
        f'<b>Reason:</b> {display_reason}'
        f'</div>'
        f'<div style="background:rgba(255,255,255,0.07);border-radius:8px;padding:12px 14px;">'
        f'<div style="font-size:13px;font-weight:600;margin-bottom:6px;opacity:0.85;text-transform:uppercase;letter-spacing:0.5px;">Next Steps</div>'
        f'<ul style="margin:0;padding-left:18px;font-size:13px;opacity:0.92;line-height:1.6;">{steps_html}</ul>'
        f'</div>'
        f'<div style="font-size:12px;opacity:0.7;margin-top:10px;border-top:1px solid rgba(255,255,255,0.15);padding-top:8px;">'
        f'This issue has been routed to a human support specialist.'
        f'</div>'
        f'</div>'
    )


def render_chat_area() -> None:
    """Render main chat interface with auto-scroll to latest message."""
    bubbles_html = ""
    for message in st.session_state.messages:
        if message.get("role") == "assistant" and message.get("escalation_triggered"):
            bubbles_html += _escalation_banner_html(message)
        bubbles_html += _bubble_html(message)

    chat_html = (
        '<div id="chat-container" style="'
        'overflow-y:auto;'
        'max-height:62vh;'
        'padding:0.5rem 0.25rem 1rem;'
        'display:flex;'
        'flex-direction:column;">'
        + bubbles_html +
        '</div>'
    )
    st.markdown(chat_html, unsafe_allow_html=True)

    js_scroll = """
  <script>
function scrollToBottom() {
    const container = document.getElementById("chat-container");
    if (!container) return;

    requestAnimationFrame(() => {
        container.scrollTop = container.scrollHeight;
    });
}

window.addEventListener("load", scrollToBottom);

setTimeout(scrollToBottom, 100);
setTimeout(scrollToBottom, 300);
setTimeout(scrollToBottom, 600);
</script>
    """
    from streamlit.components.v1 import html
    html(js_scroll, height=0)


    prompt = st.chat_input("Ask me about orders, returns, delivery, promotions, or account issues...")

    if prompt:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
                "timestamp": get_local_time_format(),
            }
        )

        with st.spinner("Searching knowledge base..."):
            reply = chat(prompt, top_k=5)

        answer = reply.get("answer") or "I couldn't generate a response at this time."
        intent = reply.get("detected_intent") or "Other Support"
        confidence = float(reply.get("confidence", 0.0))
        sources = reply.get("sources") or []
        escalation_triggered = bool(reply.get("escalation_triggered", False))
        escalation_decision = reply.get("escalation_decision") or ""
        escalation_priority = reply.get("escalation_priority") or ""
        escalation_reason = reply.get("escalation_reason") or ""

        esc_type = "general"
        if escalation_triggered or escalation_decision == "ESCALATE_TO_HUMAN":
            escalation_triggered = True
            esc_type, _ = ResponseTemplateBuilder.classify_escalation_type(
                query=prompt,
                intent=intent,
                raw_reason=escalation_reason,
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "timestamp": get_local_time_format(),
                "intent": intent,
                "confidence": confidence,
                "sources": sources,
                "escalation_triggered": escalation_triggered,
                "escalation_priority": escalation_priority,
                "escalation_reason": escalation_reason,
                "esc_type": esc_type,
            }
        )
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1].get("role") == "assistant":
        last = st.session_state.messages[-1]

        if last.get("intent") or last.get("confidence"):
            st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                if last.get("intent"):
                    intent_badge(last.get("intent"))

            with col2:
                if last.get("confidence"):
                    confidence_meter(last.get("confidence"))

        if last.get("sources"):
            st.markdown("---")
            render_sources(last.get("sources") or [])


def main() -> None:
    """Main app entry point."""
    initialize_state()

    apply_theme()

    render_sidebar()
    render_header()
    render_chat_area()


if __name__ == "__main__":
    main()
