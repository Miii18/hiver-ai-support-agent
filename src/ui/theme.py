from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0a0e1a;
            --panel: #111827;
            --panel-2: #1a2035;
            --text: #f0f4f8;
            --muted: #8b95a5;
            --accent: #2563eb;
            --accent-light: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: rgba(255,255,255,0.06);
            --border-accent: rgba(59,130,246,0.2);
            --shadow: 0 4px 24px rgba(0,0,0,0.4);
            --radius: 12px;
            --radius-lg: 16px;
            --radius-full: 9999px;
        }

        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"],
        .stApp {
            background: var(--bg) !important;
            color: var(--text);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
            max-width: 1200px;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* ── Header ─────────────────────────────────── */
        .header-banner {
            background:
                repeating-radial-gradient(circle at 20% 40%, rgba(255,255,255,0.03) 0, transparent 60px),
                linear-gradient(135deg, #1e3a8a 0%, #2563eb 55%, #3b82f6 100%);
            border-radius: var(--radius-lg);
            padding: 2rem 2.25rem;
            color: #fff;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(37,99,235,0.25);
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: var(--radius-full);
            padding: 0.35rem 0.85rem;
            font-size: 0.72rem;
            font-weight: 600;
            color: #fff;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }
        .pill-green { background: rgba(16,185,129,0.2); border-color: rgba(16,185,129,0.4); }

        /* ── Sidebar ─────────────────────────────────── */
        [data-testid="stSidebar"],
        .stSidebar {
            background: var(--panel) !important;
        }

        .status-header {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 0.6rem;
        }

        .sidebar-cat-item {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.5rem 0.65rem;
            border-radius: 8px;
            border-left: 3px solid transparent;
            font-size: 0.9rem;
            color: var(--text);
            cursor: default;
            transition: background 0.15s ease, border-color 0.15s ease;
            margin-bottom: 2px;
        }
        .sidebar-cat-item:hover {
            background: rgba(59,130,246,0.12);
            border-left-color: var(--accent-light);
        }

        .status-card {
            background: var(--panel-2);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0.9rem 1rem;
            margin-bottom: 0.5rem;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0;
            font-size: 0.88rem;
            color: var(--text);
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(16,185,129,0.12);
            color: var(--success);
            border: 1px solid rgba(16,185,129,0.3);
            border-radius: 6px;
            padding: 0.2rem 0.6rem;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: auto;
        }
        .status-badge.offline {
            background: rgba(239,68,68,0.12);
            color: var(--danger);
            border-color: rgba(239,68,68,0.3);
        }
        .dot {
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--success);
            flex-shrink: 0;
        }
        .dot.offline { background: var(--danger); }

        /* ── Chat bubbles ────────────────────────────── */

        /* Streamlit wraps st.markdown in stMarkdownContainer > p — neutralize that */
        [data-testid="stMarkdownContainer"] {
            width: 100%;
            min-width: 0;
        }
        [data-testid="stMarkdownContainer"] > p {
            margin: 0;
            padding: 0;
            width: 100%;
            min-width: 0;
        }

        .chat-row-user {
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            justify-content: flex-end;
            align-items: center;
            gap: 10px;
            margin-bottom: 1.1rem;
            width: 100%;
            box-sizing: border-box;
        }
        .chat-row-assistant {
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            justify-content: flex-start;
            align-items: center;
            gap: 10px;
            margin-bottom: 1.1rem;
            width: 100%;
            box-sizing: border-box;
        }
        .chat-bubble-wrapper {
            display: flex;
            flex-direction: column;
            min-width: 0;
            max-width: 75%;
            flex-shrink: 1;
            flex-grow: 0;
        }
        .chat-row-user .chat-bubble-wrapper {
            max-width: 70%;
        }
        .chat-row-assistant .chat-bubble-wrapper {
            max-width: 80%;
        }
        .chat-avatar {
            width: 36px;
            height: 36px;
            min-width: 36px;
            border-radius: 50%;
            background: var(--panel-2);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
            line-height: 1;
        }
        .chat-bubble-user {
            background: linear-gradient(135deg, #1d4ed8, #2563eb);
            color: #fff;
            border-radius: 18px 18px 4px 18px;
            padding: 0.75rem 1rem;
            max-width: 100%;
            min-width: 120px;
            width: fit-content;
            line-height: 1.55;
            font-size: 0.92rem;
            box-shadow: 0 2px 12px rgba(37,99,235,0.3);
            word-break: break-word;
            overflow-wrap: break-word;
            white-space: normal;
            writing-mode: horizontal-tb;
            text-orientation: mixed;
            box-sizing: border-box;
        }
        .chat-bubble-assistant {
            background: var(--panel-2);
            border: 1px solid rgba(255,255,255,0.08);
            color: var(--text);
            border-radius: 18px 18px 18px 4px;
            padding: 0.75rem 1rem;
            max-width: 100%;
            min-width: 120px;
            width: fit-content;
            line-height: 1.55;
            font-size: 0.92rem;
            word-break: break-word;
            overflow-wrap: break-word;
            white-space: normal;
            writing-mode: horizontal-tb;
            text-orientation: mixed;
            box-sizing: border-box;
        }
        .bubble-meta {
            font-size: 0.68rem;
            opacity: 0.45;
            margin-top: 0.3rem;
            white-space: nowrap;
        }
        .chat-bubble-user .bubble-meta { text-align: right; }

        /* ── Confidence ──────────────────────────────── */
        .confidence-wrap {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.9rem 1rem;
        }
        .conf-badge {
            display: inline-block;
            border-radius: var(--radius-full);
            padding: 0.2rem 0.65rem;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.3px;
        }
        .conf-high { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.35); }
        .conf-med  { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.35); }
        .conf-low  { background: rgba(239, 68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.35); }
        .conf-bar-track {
            background: rgba(255,255,255,0.08);
            border-radius: var(--radius-full);
            height: 6px;
            overflow: hidden;
            margin-top: 0.55rem;
        }
        .conf-bar-fill {
            height: 100%;
            border-radius: var(--radius-full);
            transition: width 0.4s ease;
        }
        .conf-bar-high { background: linear-gradient(90deg, #059669, #10b981); }
        .conf-bar-med  { background: linear-gradient(90deg, #d97706, #f59e0b); }
        .conf-bar-low  { background: linear-gradient(90deg, #dc2626, #ef4444); }

        /* ── Sources ─────────────────────────────────── */
        .sources-header {
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 0.6rem;
        }
        .source-card {
            background: var(--panel);
            border: 1px solid var(--border-accent);
            border-radius: var(--radius);
            padding: 0.85rem 1rem;
            margin-bottom: 0.5rem;
            transition: border-color 0.15s ease;
        }
        .source-card:hover { border-color: rgba(59,130,246,0.5); }
        .relevance-badge {
            display: inline-block;
            border-radius: var(--radius-full);
            padding: 0.15rem 0.55rem;
            font-size: 0.7rem;
            font-weight: 700;
        }
        .rel-high { background: rgba(16,185,129,0.15); color: #10b981; }
        .rel-med  { background: rgba(245,158,11,0.15); color: #f59e0b; }
        .rel-low  { background: rgba(239,68,68,0.15);  color: #ef4444; }

        /* ── Intent chip ─────────────────────────────── */
        .intent-chip {
            display: inline-block;
            background: rgba(37,99,235,0.15);
            color: var(--accent-light);
            border: 1px solid rgba(59,130,246,0.3);
            border-radius: var(--radius-full);
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 600;
        }

        /* ── Streamlit widget overrides ─────────────── */
        .stButton > button {
            border-radius: 8px !important;
            border: none !important;
            background: var(--accent) !important;
            color: #fff !important;
            font-weight: 600 !important;
            height: 2.4rem !important;
            font-size: 0.85rem !important;
            transition: background 0.15s ease !important;
        }
        .stButton > button:hover {
            background: var(--accent-light) !important;
        }
        .stDownloadButton > button {
            border-radius: 8px !important;
            border: 1px solid var(--border-accent) !important;
            background: transparent !important;
            color: var(--accent-light) !important;
            font-weight: 600 !important;
        }
        [data-testid="stChatInput"] > div {
            background: var(--panel) !important;
            border: 1px solid var(--border-accent) !important;
            border-radius: 12px !important;
        }
        [data-testid="stChatInputTextArea"] {
            color: var(--text) !important;
            background: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
