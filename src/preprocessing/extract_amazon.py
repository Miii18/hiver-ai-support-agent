
import pandas as pd
from pathlib import Path

# ==========================================================
# Hiver AI Support Agent - Amazon Dataset Extraction
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "twcs.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "interim" / "amazon_support.csv"

print("=" * 70)
print("🛒 EXTRACTING AMAZONHELP CONVERSATIONS")
print("=" * 70)

CHUNK_SIZE = 100_000

amazon_chunks = []
total_rows = 0

for chunk in pd.read_csv(RAW_DATA_PATH, chunksize=CHUNK_SIZE, low_memory=False):
    total_rows += len(chunk)

    amazon_chunk = chunk[chunk["author_id"] == "AmazonHelp"]

    if not amazon_chunk.empty:
        amazon_chunks.append(amazon_chunk)

print(f"\n📦 Total Rows Scanned : {total_rows:,}")

amazon_df = pd.concat(amazon_chunks, ignore_index=True)

print(f"🛒 AmazonHelp Tweets  : {len(amazon_df):,}")

amazon_df.to_csv(OUTPUT_PATH, index=False)

print(f"\n✅ Saved Successfully!\n{OUTPUT_PATH}")