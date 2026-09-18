"""Simple runner to start the FastAPI app with uvicorn."""
from pathlib import Path
import uvicorn

if __name__ == '__main__':
    # run from project root
    uvicorn.run("src.api.app:app", host="127.0.0.1", port=8000, reload=False)
from __future__ import annotations

import logging
import sys
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.api.config import settings
from src.api.app import app

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
LOGGER = logging.getLogger('run_api')


def run() -> int:
    LOGGER.info('Launching uvicorn for local API...')
    uvicorn.run(app, host=settings.host, port=settings.port, log_level='info')
    return 0


if __name__ == '__main__':
    sys.exit(run())
