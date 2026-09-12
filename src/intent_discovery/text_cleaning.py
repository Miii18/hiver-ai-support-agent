from __future__ import annotations

from pathlib import Path
import logging
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+", flags=re.IGNORECASE)
HASHTAG_RE = re.compile(r"#(\w+)", flags=re.UNICODE)


def _clean_series(series: pd.Series) -> pd.Series:
    """Vectorized cleaning of a pandas Series containing conversation text.

    Uses pandas string methods for performance.
    """
    s = series.fillna("").astype(str)

    # remove URLs
    s = s.str.replace(URL_RE, ' ', regex=True)

    # remove twitter mentions
    s = s.str.replace(MENTION_RE, ' ', regex=True)

    # replace hashtags keeping the word
    s = s.str.replace(HASHTAG_RE, r'\1', regex=True)

    # normalize whitespace
    s = s.str.replace(r"\s+", ' ', regex=True).str.strip()

    return s


def run_cleaning_pipeline(
    input_csv: Optional[Path] = None,
    output_csv: Optional[Path] = None,
) -> None:
    """Read raw conversations CSV, clean `conversation` into `clean_text`, and persist.

    This function validates inputs and outputs per project requirements.
    """
    if input_csv is None:
        input_csv = Path.cwd() / 'data' / 'processed' / 'amazon_conversations.csv'
    if output_csv is None:
        output_csv = Path.cwd() / 'data' / 'processed' / 'amazon_conversations_clean.csv'

    input_csv = Path(input_csv)
    output_csv = Path(output_csv)

    # 1. Validate input exists and not empty
    if not input_csv.exists():
        logger.error('Input CSV not found: %s', input_csv)
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    if input_csv.stat().st_size == 0:
        logger.error('Input CSV is empty: %s', input_csv)
        raise ValueError(f"Input CSV is empty: {input_csv}")

    # 2. Read CSV
    df = pd.read_csv(input_csv)
    n_before = len(df)
    print(f"Loaded original dataset: {n_before:,} rows")

    # 3. Validate required columns exist
    required = [
        'conversation_id',
        'root_tweet_id',
        'conversation',
        'message_count',
        'customer_message_count',
        'amazon_message_count',
        'first_tweet_id',
        'last_tweet_id',
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        logger.error('Missing required columns: %s', missing)
        raise ValueError(f"Missing required columns: {missing}")

    print('Columns validated: PASS')

    # 4. Drop duplicate conversations by conversation_id (preserve first occurrence)
    df = df.drop_duplicates(subset=['conversation_id'])

    # 5. Clean the conversation column into new column clean_text (preserve conversation)
    df['clean_text'] = _clean_series(df['conversation'])
    print('Created clean_text column.')

    # 6. Remove rows where clean_text is empty
    before_filter = len(df)
    df = df[df['clean_text'].str.strip().astype(bool)]
    after_filter = len(df)

    # 7. Save output CSV (preserve all original columns plus clean_text)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Saved {output_csv.name}")

    # 8. Post-save validations (memory-safe; do not load the full CSV)
    if not output_csv.exists():
        logger.error('Saved CSV not found: %s', output_csv)
        raise FileNotFoundError(f"Saved CSV not found: {output_csv}")

    file_size_bytes = output_csv.stat().st_size
    if file_size_bytes <= 1024:
        logger.error('Saved CSV size too small: %d bytes', file_size_bytes)
        raise AssertionError('Saved CSV too small')

    preview_df = pd.read_csv(output_csv, nrows=5, engine='python')
    if 'clean_text' not in preview_df.columns:
        logger.error('clean_text column missing after save')
        raise AssertionError('clean_text missing in saved CSV')

    row_count = sum(len(chunk) for chunk in pd.read_csv(output_csv, chunksize=5000, engine='python'))
    if row_count != len(df):
        logger.error('Row count mismatch: before=%d after_save=%d', len(df), row_count)
        raise AssertionError('Row count mismatch after saving cleaned CSV')

    file_size_mb = file_size_bytes / (1024 * 1024)
    print('Validation PASS')
    print(f'Rows saved: {row_count}')
    print(f'File size: {file_size_mb:.2f} MB')


if __name__ == '__main__':
    run_cleaning_pipeline()
