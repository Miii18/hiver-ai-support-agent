from __future__ import annotations

from pathlib import Path
import logging
import json
import time
from typing import Optional
from datetime import datetime

import numpy as np
import pandas as pd
from tqdm import tqdm

try:
    import torch
except Exception:
    torch = None

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def build_embeddings(
    input_csv: Optional[Path] = None,
    out_dir: Optional[Path] = None,
    model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',
    batch_size: int = 64,
) -> None:
    """Produce sentence embeddings and metadata for the sample dataset.

    This function is idempotent and safe to rerun. It:
    - validates the input CSV
    - loads a SentenceTransformer model (cached)
    - encodes `clean_text` in batches (skipping empty text for encoding but
      preserving order via zero placeholders)
    - normalizes embeddings and saves outputs to `out_dir`

    Outputs saved:
    - sample_sentence_embeddings.npy (np.float32)
    - sample_metadata.csv
    - embedding_info.json
    """
    start_time = time.time()

    if input_csv is None:
        input_csv = Path.cwd() / 'data' / 'processed' / 'amazon_conversations_sample.csv'
    if out_dir is None:
        out_dir = Path.cwd() / 'data' / 'embeddings'

    input_csv = Path(input_csv)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not input_csv.exists():
        logger.error('Input file not found: %s', input_csv)
        raise FileNotFoundError(f'Input file not found: {input_csv}')

    # Load dataset
    df = pd.read_csv(input_csv, encoding='utf-8')
    n_rows = len(df)
    print(f'Dataset rows: {n_rows:,}')

    if n_rows != 10_000:
        logger.error('Input must contain exactly 10,000 rows; got %d', n_rows)
        raise AssertionError('Input must contain exactly 10,000 rows')

    if 'clean_text' not in df.columns:
        logger.error('clean_text column missing')
        raise AssertionError('clean_text column missing')

    if df['conversation_id'].duplicated().any():
        logger.error('Duplicate conversation_id found')
        raise AssertionError('Duplicate conversation_id found')

    print('Dataset validation: PASS')

    # Device detection
    device_used = 'cpu'
    if torch is not None and torch.cuda.is_available():
        device_used = 'cuda'
    print(f'Selected device: {device_used}')

    # Load model (SentenceTransformer handles caching)
    model = SentenceTransformer(model_name, device=device_used)

    # Prepare input texts and metadata
    texts = df['clean_text'].fillna('').astype(str).tolist()
    meta_cols = ['conversation_id', 'root_tweet_id', 'clean_text', 'message_count']
    metadata = df[meta_cols].copy()

    # Pre-allocate embeddings array (float32)
    # We will detect embedding dimension after encoding first batch
    n = n_rows
    embedding_dim: Optional[int] = None
    embeddings = None

    # Process in batches, preserving order. For empty strings we leave zero vectors.
    for start in tqdm(range(0, n, batch_size), desc='Encoding', unit='batch'):
        end = min(n, start + batch_size)
        batch_texts = texts[start:end]

        # gather indices and texts that are non-empty
        non_empty_indices = [i for i, t in enumerate(batch_texts) if t.strip()]
        if non_empty_indices:
            to_encode = [batch_texts[i] for i in non_empty_indices]
            arr = model.encode(
                to_encode,
                batch_size=len(to_encode),
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        else:
            arr = np.zeros((0, 0), dtype=np.float32)

        # Initialize embeddings array once dimension is known
        if embedding_dim is None and arr.size:
            embedding_dim = arr.shape[1]
            embeddings = np.zeros((n, embedding_dim), dtype=np.float32)

        # Assign encoded vectors to their corresponding absolute indices
        if arr.size:
            for local_idx, vec in zip(non_empty_indices, arr):
                absolute_idx = start + local_idx
                embeddings[absolute_idx] = vec.astype(np.float32)

    if embedding_dim is None:
        # No non-empty text found; fail early
        logger.error('No non-empty text found to encode')
        raise AssertionError('No non-empty text found to encode')

    # Normalize embeddings (L2). Zero vectors remain zero.
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    nonzero = norms.squeeze() > 0
    embeddings[nonzero] = embeddings[nonzero] / norms[nonzero]

    # Save outputs
    emb_path = out_dir / 'sample_sentence_embeddings.npy'
    np.save(emb_path, embeddings.astype(np.float32))

    meta_path = out_dir / 'sample_metadata.csv'
    metadata.to_csv(meta_path, index=False, encoding='utf-8')

    info = {
        'embedding_model': model_name,
        'embedding_dimension': embedding_dim,
        'total_conversations': int(n),
        'created_timestamp': datetime.utcnow().isoformat() + 'Z',
        'device_used': device_used,
        'batch_size': int(batch_size),
    }
    info_path = out_dir / 'embedding_info.json'
    with open(info_path, 'w', encoding='utf-8') as fh:
        json.dump(info, fh, indent=2)

    # Validation
    ok = True
    if not emb_path.exists():
        logger.error('Embeddings file missing: %s', emb_path)
        ok = False

    loaded = np.load(emb_path)
    if loaded.shape != (n, embedding_dim):
        logger.error('Embeddings shape mismatch: expected=(%d,%d) got=%s', n, embedding_dim, loaded.shape)
        ok = False

    meta_loaded = pd.read_csv(meta_path, encoding='utf-8')
    if len(meta_loaded) != loaded.shape[0]:
        logger.error('Metadata rows != embeddings rows: %d != %d', len(meta_loaded), loaded.shape[0])
        ok = False

    if not info_path.exists():
        logger.error('Embedding info JSON missing')
        ok = False

    if ok:
        print('Embedding validation: PASS')
        print(f'Embeddings shape: {loaded.shape}')
        print(f'Metadata rows: {len(meta_loaded):,}')
    else:
        print('Embedding validation: FAIL')

    elapsed = time.time() - start_time
    logger.info('Total elapsed time: %.2f seconds', elapsed)


if __name__ == '__main__':
    build_embeddings()
from pathlib import Path
from typing import Iterable, Tuple
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_and_persist_embeddings(
    input_csv: Path,
    output_npy: Path,
    metadata_csv: Path,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    text_column: str = "clean_text",
    batch_size: int = 128,
):
    """Compute sentence embeddings for each row in `input_csv` and persist outputs.

    The function reads the input CSV, encodes `text_column` values using
    a SentenceTransformer model and writes a NumPy .npy file of embeddings and
    a CSV containing metadata columns.

    Args:
        input_csv: path to cleaned conversations CSV
        output_npy: path to write numpy embeddings
        metadata_csv: path to write metadata CSV
        model_name: HF model name
        text_column: column containing the text to embed
        batch_size: encoding batch size
    """
    from sentence_transformers import SentenceTransformer

    input_csv = Path(input_csv)
    output_npy = Path(output_npy)
    metadata_csv = Path(metadata_csv)

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)
    texts = df[text_column].fillna("").astype(str).tolist()

    logger.info(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    embeddings = []
    logger.info(f"Encoding {len(texts)} texts in batches of {batch_size}")
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        emb = model.encode(batch, show_progress_bar=False)
        embeddings.append(emb)

    embeddings = np.vstack(embeddings)

    output_npy.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_npy, embeddings)
    logger.info(f"Saved embeddings to {output_npy} with shape {embeddings.shape}")

    # persist metadata
    meta_columns = [
        "conversation_id",
        "root_tweet_id",
        "message_count",
        text_column,
    ]
    metadata_csv.parent.mkdir(parents=True, exist_ok=True)
    df.loc[:, meta_columns].to_csv(metadata_csv, index=False)
    logger.info(f"Saved metadata to {metadata_csv}")

    return embeddings.shape
