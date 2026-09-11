
import pandas as pd
from pathlib import Path

# ==========================================================
# Hiver AI Support Agent - Conversation Thread Builder V1
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "twcs.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "interim" / "amazon_threads.csv"

print("=" * 70)
print("🧵 BUILDING AMAZON CONVERSATION THREADS")
print("=" * 70)

# Load only required columns (memory efficient)
columns = [
    "tweet_id",
    "author_id",
    "inbound",
    "text",
    "in_response_to_tweet_id"
]

df = pd.read_csv(
    INPUT_PATH,
    usecols=columns,
    low_memory=False
)

print(f"\n📦 Total Tweets Loaded : {len(df):,}")

# Keep only conversations where AmazonHelp appears
amazon_ids = set(df[df["author_id"] == "AmazonHelp"]["tweet_id"])

thread_rows = df[
    (df["author_id"] == "AmazonHelp") |
    (df["in_response_to_tweet_id"].isin(amazon_ids))
].copy()

print(f"🛒 Amazon Related Tweets : {len(thread_rows):,}")

thread_rows.to_csv(OUTPUT_PATH, index=False)

print(f"\n✅ Saved Successfully!")
print(OUTPUT_PATH)