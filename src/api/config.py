from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
EMBED_DIR = DATA_DIR / "embeddings"
ASSETS_DIR = PROJECT_ROOT / "assets" / "intent_discovery"
REPORT_DIR = PROJECT_ROOT / "report"

API_TITLE = "Hiver AI Support Agent API"
API_VERSION = "1.0.0"

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'Hiver AI Support Agent API'
    version: str = '1.0.0'
    host: str = '127.0.0.1'
    port: int = 8000
    allowed_origins: list[str] = ['*']
    hf_cache_dir: Path = Path(r'D:/AI/hf_cache')

    class Config:
        env_prefix = 'HIVER_'


settings = Settings()
