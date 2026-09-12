from pathlib import Path
import re
from typing import Optional

# Text cleaning helpers for EDA and later phases.
# Keep functions small and well-documented for reuse in the pipeline.

URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+", flags=re.IGNORECASE)
HASHTAG_RE = re.compile(r"#\w+", flags=re.IGNORECASE)
EMOJI_RE = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]+", flags=re.UNICODE)
PUNCT_RE = re.compile(r"[^
\w\sÀ-ÿ]+", flags=re.UNICODE)


def basic_clean(text: Optional[str]) -> str:
    """Perform a deterministic, reversible-light cleaning on text for EDA.

    Steps:
    - Replace URLs and mentions with a single token placeholder.
    - Remove punctuation (keeps accented characters).
    - Collapse whitespace.

    This function does NOT lowercase text to preserve language detection signals.
    """
    if not text:
        return ""

    text = str(text)
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = HASHTAG_RE.sub(" ", text)
    text = EMOJI_RE.sub(" ", text)
    text = PUNCT_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def aggressive_clean(text: Optional[str]) -> str:
    """Aggressive cleaning for building the final customer corpus.

    Steps:
    - Lowercase
    - Remove URLs, mentions, hashtags
    - Remove punctuation
    - Keep alphabetic and accented words
    - Collapse whitespace
    """
    if not text:
        return ""

    text = str(text).lower()
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = HASHTAG_RE.sub(" ", text)
    text = EMOJI_RE.sub(" ", text)

    # Keep letters (including accents) and numbers, remove remaining punctuation
    text = re.sub(r"[^\w\sÀ-ÿ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_customer_messages(conversation_text: Optional[str]) -> str:
    """Extract and join customer messages from a full conversation string.

    The conversation_text format is expected as:
    "Customer:\n...\n\nAmazon:\n...\n"

    This function preserves the order of customer messages and returns a single combined string.
    """
    if not conversation_text:
        return ""

    lines = [line.strip() for line in conversation_text.splitlines() if line.strip()]
    customer_parts = []
    current_speaker = None
    buffer = []

    for line in lines:
        if line.endswith(":"):
            if current_speaker == "Customer" and buffer:
                customer_parts.append(" ".join(buffer))
            buffer = []
            if line.startswith("Customer:"):
                current_speaker = "Customer"
            elif line.startswith("Amazon:"):
                current_speaker = "Amazon"
            else:
                current_speaker = None
            continue

        if current_speaker == "Customer":
            buffer.append(line)

    if current_speaker == "Customer" and buffer:
        customer_parts.append(" ".join(buffer))

    return " \n ".join(customer_parts)
