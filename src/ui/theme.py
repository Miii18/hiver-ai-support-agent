from __future__ import annotations

import streamlit as st


def apply_theme(use_dark: bool = True) -> None:
    """Apply polished dark/light branding to the Streamlit app."""
    accent = "#ff9900" if use_dark else "#ff7a00"
    bg = "#0b1220" if use_dark else "#f5f7fb"
    panel = "#121c2b" if use_dark else "#ffffff"
    text = "#eaf2ff" if use_dark else "#17212b"
    muted = "#9db0c9" if use_dark else "#53657d"
    border = "rgba(255,255,255,0.08)" if use_dark else "rgba(23,33,43,0.08)"

    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {bg};
            --panel: {panel};
            --text: {text};
            --muted: {muted};
            --accent: {accent};
            --border: {border};
        }}
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
            background: var(--bg);
            color: var(--text);
        }}
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        .stApp {{
            background: linear-gradient(180deg, rgba(255,153,0,0.08), transparent 25%), var(--bg);
        }}
        .card {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        }}
        .welcome-banner {{
            background: linear-gradient(135deg, #ff9900, #ffb347);
            border-radius: 20px;
            padding: 1.25rem 1.5rem;
            color: #111827;
            font-weight: 700;
            box-shadow: 0 12px 30px rgba(255,153,0,0.22);
        }}
        .status-pill {{
            display: inline-block;
            background: rgba(255,153,0,0.16);
            color: var(--accent);
            border: 1px solid rgba(255,153,0,0.45);
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-size: 0.72rem;
            font-weight: 700;
        }}
        .source-card {{
            background: rgba(255,153,0,0.06);
            border: 1px solid rgba(255,153,0,0.25);
            border-radius: 14px;
            padding: 0.8rem 0.9rem;
            margin-top: 0.5rem;
        }}
        .chat-message-user {{
            background: rgba(255,153,0,0.15);
            border: 1px solid rgba(255,153,0,0.28);
            border-radius: 0.8rem;
            padding: 0.75rem 0.85rem;
        }}
        .chat-message-assistant {{
            background: rgba(148,163,184,0.08);
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 0.8rem;
            padding: 0.75rem 0.85rem;
        }}
        .metric-box {{
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.8rem;
        }}
        .stSidebar {{
            background: rgba(12,18,26,0.9);
        }}
        .stButton > button {{
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #ff9900, #ffb347);
            color: #111827;
            font-weight: 700;
        }}
        div[data-testid="stDownloadButton"] > button {{
            border-radius: 12px;
            border: none;
            background: rgba(255,153,0,0.08);
            color: var(--text);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
