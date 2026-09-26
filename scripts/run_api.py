"""Run the FastAPI server for the Hiver AI Support Agent."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import uvicorn

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

LOGGER = logging.getLogger("run_api")


def run() -> int:
    """Launch the FastAPI application with Uvicorn."""
    LOGGER.info("Launching Hiver AI Support Agent API...")

    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", settings.port)),
        log_level="info",
        reload=False,
    )

    return 0


if __name__ == "__main__":
    sys.exit(run())