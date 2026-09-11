
import pandas as pd
from pathlib import Path

# ==========================================================
# Hiver AI Support Agent - Dataset Inspector V1
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "twcs.csv"

print("=" * 70)
print("📊 HIVER AI SUPPORT AGENT - DATASET INSPECTOR V1")
print("=" * 70)

print(f"\n📂 Reading dataset from:\n{RAW_DATA_PATH}")

# Read dataset
df = pd.read_csv(
    RAW_DATA_PATH,
    low_memory=False
)

print("\n✅ Dataset Loaded Successfully!")

# ----------------------------------------------------------
# Basic Information
# ----------------------------------------------------------

print("\n📦 DATASET SHAPE")
print("-" * 30)
print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]}")

print("\n🧾 COLUMN NAMES")
print("-" * 30)

for i, col in enumerate(df.columns, start=1):
    print(f"{i}. {col}")

print("\n🔍 FIRST 5 ROWS")
print("-" * 30)
print(df.head())

print("\n📋 DATA TYPES")
print("-" * 30)
print(df.dtypes)

print("\n❓ MISSING VALUES")
print("-" * 30)
print(df.isnull().sum())

print("\n💾 MEMORY USAGE")
print("-" * 30)
memory = df.memory_usage(deep=True).sum() / (1024**2)
print(f"{memory:.2f} MB")

print("\n🎉 Inspection Complete!")