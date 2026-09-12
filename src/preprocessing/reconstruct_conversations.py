import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

# ==========================================================
# HIVER AI SUPPORT AGENT
# Phase 2 — Production Conversation Reconstruction
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "twcs.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "amazon_conversations.csv"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "tweet_id",
    "author_id",
    "text",
    "in_response_to_tweet_id",
]


# ----------------------------------------------------------
# STEP 1 — Load Dataset
# ----------------------------------------------------------

def load_dataset(input_path: Path) -> pd.DataFrame:
    """Load the raw tweet dataset with just the columns required for reconstruction."""
    logger.info("STEP 1 — Load Dataset")
    logger.info("Loading raw Twitter support dataset...")

    df = pd.read_csv(
        input_path,
        usecols=REQUIRED_COLUMNS,
        dtype={
            "tweet_id": "Int64",
            "in_response_to_tweet_id": "Int64",
            "author_id": "string",
            "text": "string",
        },
        low_memory=False,
    )

    logger.info("Dataset loaded successfully.")
    logger.info(f"Total tweets loaded: {len(df):,}")
    return df


# ----------------------------------------------------------
# STEP 2 — Build Lookup Tables
# ----------------------------------------------------------

def build_lookup_tables(
    df: pd.DataFrame,
) -> tuple[dict[int, dict[str, Any]], dict[int, list[int]], dict[int, int]]:
    """Build O(1) lookup structures for tweet content, child replies, and parent links."""
    logger.info("STEP 2 — Build Lookup Tables")

    tweet_lookup: dict[int, dict[str, Any]] = {}
    parent_lookup: dict[int, int] = {}
    children_map: dict[int, list[int]] = defaultdict(list)

    # Dictionary lookups avoid repeated DataFrame scans over millions of rows.
    for row in df.itertuples(index=False):
        tweet_id = int(row.tweet_id)
        parent_id = row.in_response_to_tweet_id

        tweet_lookup[tweet_id] = {
            "tweet_id": tweet_id,
            "author_id": row.author_id,
            "text": row.text,
            "in_response_to_tweet_id": parent_id,
        }

        if pd.notna(parent_id):
            parent_int = int(parent_id)
            parent_lookup[tweet_id] = parent_int
            children_map[parent_int].append(tweet_id)

    for parent_id in children_map:
        children_map[parent_id].sort()

    logger.info(f"Tweet lookup size: {len(tweet_lookup):,}")
    logger.info(f"Parent lookup size: {len(parent_lookup):,}")
    logger.info(f"Children adjacency size: {len(children_map):,}")
    return tweet_lookup, children_map, parent_lookup


# ----------------------------------------------------------
# STEP 3 — Root Detection
# ----------------------------------------------------------

def find_root(tweet_id: int, tweet_lookup: dict[int, dict[str, Any]]) -> int:
    """Walk backward through parent links until the root tweet is found or the chain ends."""
    current = int(tweet_id)
    visited: set[int] = set()

    while True:
        if current in visited:
            return current
        visited.add(current)

        tweet = tweet_lookup.get(current)
        if tweet is None:
            return current

        parent_id = tweet.get("in_response_to_tweet_id")
        if pd.isna(parent_id):
            return current

        parent_int = int(parent_id)
        if parent_int not in tweet_lookup:
            return current

        current = parent_int


# ----------------------------------------------------------
# STEP 4 — DFS Traversal
# ----------------------------------------------------------

def build_conversation(
    root_id: int,
    tweet_lookup: dict[int, dict[str, Any]],
    children_map: dict[int, list[int]],
) -> list[dict[str, Any]]:
    """Iteratively traverse a conversation tree and return messages in deterministic reply order."""
    messages: list[dict[str, Any]] = []
    stack: list[tuple[int, int]] = [(root_id, 0)]
    visited: set[int] = set()

    while stack:
        current_id, depth = stack.pop()
        if current_id in visited:
            continue
        visited.add(current_id)

        tweet = tweet_lookup.get(current_id)
        if tweet is None:
            continue

        author_id = str(tweet.get("author_id") or "")
        speaker = "Customer" if author_id != "AmazonHelp" else "Amazon"
        message = {
            "tweet_id": current_id,
            "author_id": author_id,
            "speaker": speaker,
            "text": str(tweet.get("text") or "").strip(),
            "depth": depth,
        }
        messages.append(message)

        child_ids = children_map.get(current_id, [])
        if child_ids:
            # Sort ensures deterministic ordering. Reversing keeps the leftmost child at the top of the stack.
            for child_id in reversed(child_ids):
                stack.append((child_id, depth + 1))

    return messages


# ----------------------------------------------------------
# STEP 5 — Conversation Reconstruction
# ----------------------------------------------------------

def format_conversation(messages: list[dict[str, Any]]) -> str:
    """Create the final conversational text block in the requested format."""
    parts: list[str] = []
    for message in messages:
        speaker = message["speaker"]
        text = message["text"]
        parts.append(f"{speaker}:\n{text}")
    return "\n\n".join(parts)


def summarize_conversation(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute message-level metrics for a reconstructed conversation."""
    if not messages:
        return {
            "message_count": 0,
            "customer_message_count": 0,
            "amazon_message_count": 0,
            "first_tweet_id": None,
            "last_tweet_id": None,
        }

    customer_count = sum(1 for message in messages if message["speaker"] == "Customer")
    amazon_count = sum(1 for message in messages if message["speaker"] == "Amazon")

    return {
        "message_count": len(messages),
        "customer_message_count": customer_count,
        "amazon_message_count": amazon_count,
        "first_tweet_id": messages[0]["tweet_id"],
        "last_tweet_id": messages[-1]["tweet_id"],
    }


def reconstruct_amazon_conversations(
    df: pd.DataFrame,
    tweet_lookup: dict[int, dict[str, Any]],
    children_map: dict[int, list[int]],
) -> list[dict[str, Any]]:
    """Find all AmazonHelp-rooted conversations exactly once and keep only valid ones."""
    logger.info("STEP 5 — Conversation Reconstruction")
    amazon_ids = sorted({int(tweet_id) for tweet_id in df.loc[df["author_id"] == "AmazonHelp", "tweet_id"].tolist()})

    reconstructed: list[dict[str, Any]] = []
    visited_roots: set[int] = set()

    logger.info(f"Found {len(amazon_ids):,} AmazonHelp tweets to process.")

    for index, amazon_id in enumerate(amazon_ids, start=1):
        root_id = find_root(amazon_id, tweet_lookup)
        if root_id in visited_roots:
            continue
        visited_roots.add(root_id)

        conversation_messages = build_conversation(root_id, tweet_lookup, children_map)
        if not conversation_messages:
            continue

        has_amazon = any(message["author_id"] == "AmazonHelp" for message in conversation_messages)
        if not has_amazon:
            continue

        reconstructed.append(
            {
                "root_tweet_id": root_id,
                "messages": conversation_messages,
            }
        )

        if index % 5000 == 0:
            logger.info(f"Processed {index:,} AmazonHelp roots; reconstructed {len(reconstructed):,} conversations.")

    logger.info(f"Final reconstructed conversations: {len(reconstructed):,}")
    return reconstructed


# ----------------------------------------------------------
# STEP 6 — Validation
# ----------------------------------------------------------

def validate_conversations(df: pd.DataFrame, tweet_lookup: dict[int, dict[str, Any]]) -> dict[str, bool]:
    """Run reproducible data quality checks on the final conversation dataset."""
    logger.info("STEP 6 — Validation")

    checks: dict[str, bool] = {}
    checks["No duplicate conversation IDs"] = not df["conversation_id"].duplicated().any()
    checks["No duplicate root tweets"] = not df["root_tweet_id"].duplicated().any()
    checks["Every conversation contains AmazonHelp"] = df["conversation"].str.contains("Amazon:", na=False).all()
    checks["No empty conversation text"] = (df["conversation"].str.len() > 0).all()

    starts_with_customer = []
    for row in df.itertuples(index=False):
        root_id = int(row.root_tweet_id)
        root_tweet = tweet_lookup.get(root_id)
        root_author = str(root_tweet.get("author_id") or "") if root_tweet is not None else ""

        if root_author == "AmazonHelp":
            starts_with_customer.append(True)
            continue

        starts_with_customer.append(row.conversation.startswith("Customer:"))

    checks["Every conversation starts with Customer whenever possible"] = all(starts_with_customer)

    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        logger.info(f"{name}: {status}")

    return checks


# ----------------------------------------------------------
# STEP 7 — Save Dataset
# ----------------------------------------------------------

def save_conversations(conversations: list[dict[str, Any]], output_path: Path) -> pd.DataFrame:
    """Persist the final conversation dataset to disk with stable conversation IDs and required schema."""
    logger.info("STEP 7 — Save Dataset")

    rows: list[dict[str, Any]] = []
    for conversation_index, item in enumerate(conversations, start=1):
        root_id = int(item["root_tweet_id"])
        messages = item["messages"]
        summary = summarize_conversation(messages)
        conversation_text = format_conversation(messages)

        rows.append(
            {
                "conversation_id": f"AMZ_{conversation_index:06d}",
                "root_tweet_id": root_id,
                "conversation": conversation_text,
                "message_count": summary["message_count"],
                "customer_message_count": summary["customer_message_count"],
                "amazon_message_count": summary["amazon_message_count"],
                "first_tweet_id": summary["first_tweet_id"],
                "last_tweet_id": summary["last_tweet_id"],
            }
        )

    output_df = pd.DataFrame(
        rows,
        columns=[
            "conversation_id",
            "root_tweet_id",
            "conversation",
            "message_count",
            "customer_message_count",
            "amazon_message_count",
            "first_tweet_id",
            "last_tweet_id",
        ],
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(output_df):,} conversations to {output_path}")
    return output_df


def print_summary(df: pd.DataFrame) -> None:
    """Print quality metrics and sample reconstructed conversations for review."""
    logger.info("\n=== Final Dataset Summary ===")
    logger.info(f"Total conversations: {len(df):,}")
    logger.info(f"Average messages per conversation: {df['message_count'].mean():.2f}")
    logger.info(f"Median messages: {df['message_count'].median():.2f}")
    logger.info(f"Maximum conversation length: {df['message_count'].max()}")
    logger.info(f"Minimum conversation length: {df['message_count'].min()}")

    logger.info("\nFirst 3 reconstructed conversations:")
    for index in range(min(3, len(df))):
        row = df.iloc[index]
        logger.info(f"\n--- Conversation {index + 1} ---")
        logger.info(row["conversation"])


def main() -> None:
    """Execute the full Amazon conversation reconstruction pipeline."""
    logger.info("=" * 90)
    logger.info("HIVER AI SUPPORT AGENT — FINAL CONVERSATION RECONSTRUCTION")
    logger.info("=" * 90)

    df = load_dataset(INPUT_PATH)
    tweet_lookup, children_map, _ = build_lookup_tables(df)

    amazon_conversations = reconstruct_amazon_conversations(df, tweet_lookup, children_map)
    final_df = save_conversations(amazon_conversations, OUTPUT_PATH)

    validate_conversations(final_df, tweet_lookup)
    print_summary(final_df)

    logger.info("\nPipeline complete.")


if __name__ == "__main__":
    main()
