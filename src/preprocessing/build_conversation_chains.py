
import pandas as pd
from pathlib import Path

# ==========================================================
# HIVER AI SUPPORT AGENT
# Phase 2.2 - Conversation Chain Builder
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "twcs.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "amazon_threads_v2.csv"

print("=" * 70)
print("🧵 PHASE 2.2 — BUILDING AMAZON CONVERSATION CHAINS")
print("=" * 70)

# ----------------------------------------------------------
# STEP 1 — Load Dataset
# ----------------------------------------------------------

# ----------------------------------------------------------
# STEP 1 — Load Full Twitter Dataset
# ----------------------------------------------------------

columns = [
    "tweet_id",
    "author_id",
    "inbound",
    "created_at",
    "text",
    "response_tweet_id",
    "in_response_to_tweet_id"
]

df = pd.read_csv(
    INPUT_PATH,
    usecols=columns,
    low_memory=False
)

print(f"\n✅ Total Twitter Tweets Loaded : {len(df):,}")

# Keep Amazon tweets + customer tweets connected to Amazon
amazon_tweet_ids = set(df[df["author_id"] == "AmazonHelp"]["tweet_id"])

df = df[
    (df["author_id"] == "AmazonHelp") |
    (df["in_response_to_tweet_id"].isin(amazon_tweet_ids))
].copy()

print(f"🛒 Amazon Conversation Tweets : {len(df):,}")

print("\nColumns Available:")
print(df.columns.tolist())


# ----------------------------------------------------------
# STEP 2 — Build Tweet Lookup Dictionary
# ----------------------------------------------------------

tweet_lookup = {}

for _, row in df.iterrows():
    tweet_lookup[row["tweet_id"]] = row

print("\n✅ Tweet Lookup Dictionary Created!")
print(f"Dictionary Size : {len(tweet_lookup):,}")



# ----------------------------------------------------------
# STEP 3 — Find Root Tweets
# ----------------------------------------------------------

root_tweets = df[df["in_response_to_tweet_id"].isna()].copy()

print("\n🌱 Root Tweets Found!")
print(f"Root Conversations : {len(root_tweets):,}")

print("\nFirst 5 Root Tweets:\n")

print(root_tweets[["tweet_id", "author_id", "text"]].head())