
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Locate project root automatically
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "twcs.csv"

print("=" * 60)
print("🚀 Hiver AI Support Agent - Dataset Loader")
print("=" * 60)

print(f"📂 Looking for dataset at:\n{RAW_DATA_PATH}")

# --------------------------------------------------
# Load only first 5 rows (safe for huge dataset)
# --------------------------------------------------
df = pd.read_csv(RAW_DATA_PATH, nrows=5)

print("\n✅ Dataset loaded successfully!\n")

print("📊 Shape of loaded sample:")
print(df.shape)

print("\n🧾 Columns:")
for column in df.columns:
    print(f" - {column}")

print("\n🔍 First 5 Rows:")
print(df.head())