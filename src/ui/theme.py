from __future__ import annotations

import streamlit as st


def apply_theme(use_dark: bool = True) -> None:
    """Apply production SaaS styling to the Streamlit app."""
    if use_dark:
        bg = "#0f1419"
        panel = "#1a1f2e"
        text = "#f0f4f8"
        muted = "#8b95a5"
        accent = "#2563eb"
        accent_light = "#3b82f6"
        success = "#10b981"
        border = "rgba(255,255,255,0.06)"
    else:
        bg = "#ffffff"
        panel = "#f9fafb"
        text = "#1f2937"
        muted = "#6b7280"
        accent = "#2563eb"
        accent_light = "#3b82f6"
        success = "#10b981"
        border = "rgba(0,0,0,0.08)"

    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {bg};
            --panel: {panel};
            --text: {text};
            --muted: {muted};
            --accent: {accent};
            --accent-light: {accent_light};
            --success: {success};
            --border: {border};
        }}
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
            background: var(--bg);
            color: var(--text);
        }}
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }}
        .stApp {{
            background: var(--bg);
        }}
        .card {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .status-card {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .status-header {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.75rem;
        }}
        .status-item {{
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
            font-size: 0.95rem;
        }}
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(16,185,129,0.1);
            color: var(--success);
            border: 1px solid rgba(16,185,129,0.3);
            border-radius: 6px;
            padding: 0.35rem 0.75rem;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: auto;
        }}
        .status-badge.offline {{
            background: rgba(239,68,68,0.1);
            color: #ef4444;
            border-color: rgba(239,68,68,0.3);
        }}
        .dot {{
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--success);
            margin-right: 0.4rem;
        }}
        .dot.offline {{
            background: #ef4444;
        }}
        .header-banner {{
            background: linear-gradient(135deg, var(--accent), var(--accent-light));
            border-radius: 12px;
            padding: 1.5rem;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(37,99,235,0.15);
        }}
        .header-banner h1 {{
            margin: 0;
            font-size: 1.75rem;
            font-weight: 700;
        }}
        .header-banner p {{
            margin: 0.5rem 0 0 0;
            font-size: 0.95rem;
            opacity: 0.95;
        }}
        .source-card {{
            background: rgba(37,99,235,0.05);
            border: 1px solid rgba(37,99,235,0.2);
            border-radius: 10px;
            padding: 0.9rem;
            margin-top: 0.5rem;
        }}
        .chat-message-user {{
            background: rgba(37,99,235,0.1);
            border: 1px solid rgba(37,99,235,0.2);
            border-radius: 10px;
            padding: 0.9rem;
        }}
        .chat-message-assistant {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.9rem;
        }}
        .confidence-bar {{
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 999px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        .confidence-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--accent-light));
            border-radius: 999px;
        }}
        .intent-badge {{
            display: inline-block;
            background: rgba(37,99,235,0.1);
            color: var(--accent);
            border: 1px solid rgba(37,99,235,0.3);
            border-radius: 6px;
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }}
        .stButton > button {{
            border-radius: 8px;
            border: none;
            background: var(--accent);
            color: white;
            font-weight: 600;
            height: 2.5rem;
        }}
        .stButton > button:hover {{
            background: var(--accent-light);
        }}
        .stSidebar {{
            background: var(--panel);
        }}
        .stSidebar [data-testid="stSidebar"] {{
            background: var(--panel);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
