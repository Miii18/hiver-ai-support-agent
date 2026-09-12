from __future__ import annotations

from pathlib import Path
import logging
import time
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def create_sample_dataset(
    input_csv: Optional[Path] = None,
    output_csv: Optional[Path] = None,
    sample_size: int = 10_000,
    random_state: int = 42,
) -> None:
    """Create a reproducible sample CSV from the cleaned conversations dataset.

    - Loads `input_csv` (defaults to data/processed/amazon_conversations_clean.csv)
    - Samples exactly `sample_size` rows using `random_state`
    - Preserves all columns and multilingual content
    - Saves UTF-8 CSV to `output_csv`

    Prints original rows, sample rows, sample percentage and file size.
    Performs lightweight validations (row count, unique conversation_id, clean_text present).
    """
    start = time.time()

    if input_csv is None:
        input_csv = Path.cwd() / 'data' / 'processed' / 'amazon_conversations_clean.csv'
    if output_csv is None:
        output_csv = Path.cwd() / 'data' / 'processed' / 'amazon_conversations_sample.csv'

    input_csv = Path(input_csv)
    output_csv = Path(output_csv)

    if not input_csv.exists():
        logger.error('Input CSV not found: %s', input_csv)
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    # Load cleaned dataset (this operation is expected and acceptable for Phase 4 sampling)
    df = pd.read_csv(input_csv, encoding='utf-8')
    n_orig = len(df)
    print(f'Original rows: {n_orig:,}')

    if n_orig < sample_size:
        logger.error('Not enough rows to sample: requested=%d available=%d', sample_size, n_orig)
        raise ValueError(f"Not enough rows to sample: requested={sample_size} available={n_orig}")

    # Sample reproducibly
    sample_df = df.sample(n=sample_size, random_state=random_state)

    # Validations
    if 'clean_text' not in sample_df.columns:
        logger.error('clean_text column missing in sampled dataframe')
        raise AssertionError('clean_text column missing in sampled dataframe')

    if sample_df['conversation_id'].duplicated().any():
        logger.error('Duplicate conversation_id found in sample')
        raise AssertionError('Duplicate conversation_id found in sample')

    if len(sample_df) != sample_size:
        logger.error('Sample size mismatch: expected=%d actual=%d', sample_size, len(sample_df))
        raise AssertionError('Sample size mismatch')

    # Ensure output directory exists
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    # Save UTF-8 csv
    sample_df.to_csv(output_csv, index=False, encoding='utf-8')

    file_size_bytes = output_csv.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)

    pct = (sample_size / n_orig) * 100.0

    print(f'Sample rows: {sample_size:,}')
    print(f'Sample percentage: {pct:.4f}%')
    print(f'File size: {file_size_mb:.2f} MB')

    elapsed = time.time() - start
    logger.info('Elapsed time: %.2f seconds', elapsed)
    if elapsed > 15:
        logger.warning('Runtime exceeded 15 seconds: %.2f s', elapsed)


if __name__ == '__main__':
    create_sample_dataset()
