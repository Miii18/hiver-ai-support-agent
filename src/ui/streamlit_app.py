from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
import pytz

import streamlit as st

from src.ui.api_client import chat, fetch_intents, health_check, reset_memory
from src.ui.components import (
    api_status_display,
    confidence_meter,
    embedding_model_display,
    get_display_intent,
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
    if "theme_dark" not in st.session_state:
        st.session_state.theme_dark = True


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

        intent_options = fetch_intents()
        if intent_options:
            intent_list = [
                item.get("intent_label") or item.get("name") or "Support"
                for item in intent_options[:8]
            ]
            for intent in intent_list:
                display_name = get_display_intent(intent)
                st.markdown(f"• {display_name}", unsafe_allow_html=True)

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("New Chat", use_container_width=True):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "New conversation started. How can I help you today?",
                        "timestamp": get_local_time_format(),
                    }
                ]
                st.rerun()

        with col2:
            if st.button("Clear", use_container_width=True):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Conversation cleared. Ask me anything.",
                        "timestamp": get_local_time_format(),
                    }
                ]
                st.rerun()

        if st.button("Reset Memory", use_container_width=True):
            reset_memory()
            st.info("Conversation memory cleared on server.", icon="OK")

        st.markdown("---")

        st.markdown("**Display**", unsafe_allow_html=True)
        st.session_state.theme_dark = st.toggle(
            "Dark mode",
            value=st.session_state.theme_dark,
            label_visibility="collapsed",
        )

        st.markdown("---")
        chat_log = "\n\n".join(
            f"{msg['role'].upper()} ({msg.get('timestamp', '')}):\n{msg['content']}"
            for msg in st.session_state.messages
        )
        st.download_button(
            label="Export Conversation",
            data=chat_log,
            file_name="support_conversation.txt",
            mime="text/plain",
            use_container_width=True,
        )


def render_header() -> None:
    """Render production header banner."""
    st.markdown(
        """
        <div class="header-banner">
            <h1>AI Support Assistant</h1>
            <p>Intelligent customer support powered by retrieval-augmented generation</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_area() -> None:
    """Render main chat interface with auto-scroll to latest message."""
    # Create a container for chat messages to enable scrolling
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            render_chat_bubble(message["role"], message["content"], message.get("timestamp"))

        # Invisible anchor at the bottom of chat for scroll target
        st.markdown('<div id="chat-bottom"></div>', unsafe_allow_html=True)

    # Auto-scroll to anchor using st.components.v1.html with observer
    st.components.v1.html("""
    <script>
    // Keep chat scrolled to newest message
    (function() {
        function scrollToBottom() {
            const anchor = document.getElementById('chat-bottom');
            if (anchor) {
                anchor.scrollIntoView({behavior: 'smooth', block: 'end'});
            }
        }

        // Initial scroll after small delay to ensure DOM is ready
        setTimeout(scrollToBottom, 30);

        // Also scroll after a longer delay to catch Streamlit reruns
        setTimeout(scrollToBottom, 200);

        // Observer to keep chat pinned to bottom during DOM changes
        try {
            const observer = new MutationObserver(function() {
                const anchor = document.getElementById('chat-bottom');
                if (anchor) {
                    anchor.scrollIntoView({behavior: 'auto', block: 'end'});
                }
            });

            // Observe the main app container for changes
            const appRoot = document.querySelector('[data-testid="stAppViewContainer"]');
            if (appRoot) {
                observer.observe(appRoot, {
                    childList: true,
                    subtree: true,
                    characterData: false
                });
            }
        } catch (e) {
            // Observer not critical, continue without it
        }
    })();
    </script>
    """, height=0)

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

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "timestamp": get_local_time_format(),
                "intent": intent,
                "confidence": confidence,
                "sources": sources,
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

    # Final scroll to ensure latest message is visible after all content renders
    st.components.v1.html("""
    <script>
    // Final scroll after all elements have rendered
    (function() {
        function scrollToBottom() {
            const anchor = document.getElementById('chat-bottom');
            if (anchor) {
                anchor.scrollIntoView({behavior: 'smooth', block: 'end'});
            }
        }
        setTimeout(scrollToBottom, 100);

        // Extra scroll for late-rendering content
        setTimeout(scrollToBottom, 300);
    })();
    </script>
    """, height=0)


def main() -> None:
    """Main app entry point."""
    initialize_state()

    use_dark = st.session_state.get("theme_dark", True)
    apply_theme(use_dark)

    render_sidebar()
    render_header()
    render_chat_area()


if __name__ == "__main__":
    main()
