from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime

import streamlit as st

from src.ui.api_client import chat, fetch_intents, health_check, reset_memory
from src.ui.components import (
    confidence_meter,
    intent_badge,
    render_chat_bubble,
    render_sources,
    status_pill,
)
from src.ui.theme import apply_theme


st.set_page_config(page_title="Hiver AI Support Agent", page_icon="🤖", layout="wide")


def initialize_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I’m Hiver AI Support Agent. Ask me anything about orders, returns, delivery, or account issues.",
                "timestamp": datetime.utcnow().strftime("%H:%M"),
            }
        ]
    if "theme_dark" not in st.session_state:
        st.session_state.theme_dark = True


def app_header() -> None:
    st.sidebar.title("Hiver AI Support Agent")
    st.sidebar.markdown("### Customer support intelligence")
    st.sidebar.button("New Chat", key="new_chat_button", use_container_width=True)

    if st.sidebar.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Conversation cleared. Ask a new question.",
                "timestamp": datetime.utcnow().strftime("%H:%M"),
            }
        ]

    with st.sidebar:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Phase**: 9")
        status_pill("API online" if health_check() else "API offline", health_check())
        st.markdown("**Retriever**: Loaded" if health_check() else "**Retriever**: Unavailable")
        st.markdown("</div>", unsafe_allow_html=True)

    intent_options = fetch_intents()
    if intent_options:
        st.sidebar.caption("Live intent catalog")
        for item in intent_options[:6]:
            st.sidebar.write(f"- {item.get('intent_label') or item.get('name') or 'Intent'}")


def export_chat() -> None:
    chat_log = "\n\n".join(
        f"{msg['role'].upper()} ({msg.get('timestamp', '')}):\n{msg['content']}" for msg in st.session_state.messages
    )
    st.download_button(
        label="Export Chat",
        data=chat_log,
        file_name="hiver_chat_export.txt",
        mime="text/plain",
    )


def render_main() -> None:
    use_dark = st.session_state.get("theme_dark", True)
    apply_theme(use_dark)

    st.markdown(
        """
        <div class="welcome-banner">
            Welcome to Hiver AI Support Agent.<br>
            Your production AI customer support assistant is live.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_left:
        st.write("")
    with col_center:
        st.caption("Advanced intent routing • Retrieval-augmented answers • Human-friendly replies")
    with col_right:
        st.write("")

    st.write("\n")
    for message in st.session_state.messages:
        render_chat_bubble(message["role"], message["content"], message.get("timestamp"))

    if "pending_response" in st.session_state and st.session_state.pending_response:
        with st.spinner("Thinking..."):
            st.markdown("<div class='chat-message-assistant'>Generating response…</div>", unsafe_allow_html=True)

    prompt = st.chat_input("Ask Hiver about an order, refund, delivery, account, or product issue")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": datetime.utcnow().strftime("%H:%M")})
        st.session_state.pending_response = True
        with st.spinner("Searching the knowledge base..."):
            reply = chat(prompt, top_k=5)
        st.session_state.pending_response = False

        answer = reply.get("answer") or "I could not generate a response right now."
        intent = reply.get("detected_intent") or "General"
        confidence = float(reply.get("confidence", 0.0))
        sources = reply.get("sources") or []
        rendered = {
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.utcnow().strftime("%H:%M"),
            "intent": intent,
            "confidence": confidence,
            "sources": sources,
        }
        st.session_state.messages.append(rendered)
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1].get("role") == "assistant":
        last = st.session_state.messages[-1]
        st.write("\n")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        intent_badge(last.get("intent"))
        confidence_meter(last.get("confidence"))
        render_sources(last.get("sources") or [])
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    initialize_state()
    app_header()

    st.sidebar.markdown("---")
    st.sidebar.write("Theme")
    st.session_state.theme_dark = st.sidebar.toggle("Dark mode", value=st.session_state.theme_dark)
    export_chat()
    if st.sidebar.button("Reset memory", use_container_width=True):
        reset_memory()

    render_main()


if __name__ == "__main__":
    main()
