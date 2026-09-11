
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

THREAD_PATH = PROJECT_ROOT / "data" / "interim" / "amazon_threads.csv"

df = pd.read_csv(THREAD_PATH)

print("=" * 60)
print("🧵 SAMPLE AMAZON CONVERSATIONS")
print("=" * 60)

print(df.sample(10, random_state=42)[
    ["author_id", "text", "in_response_to_tweet_id"]
])