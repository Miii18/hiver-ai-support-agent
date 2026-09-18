from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from . import config
from .routes import router as api_router

logging.getLogger("uvicorn.error").handlers.clear()
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title=config.API_TITLE, version=config.API_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.on_event("startup")
    def startup_event():
        logger.info("Starting Hiver AI Support Agent API")

    return app


app = create_app()

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.api.config import settings

LOGGER = logging.getLogger('api.app')


def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name, version=settings.version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    @app.on_event('startup')
    def startup() -> None:  # pragma: no cover - executed in server
        LOGGER.info('Starting %s v%s', settings.project_name, settings.version)

    @app.on_event('shutdown')
    def shutdown() -> None:  # pragma: no cover - executed in server
        LOGGER.info('Shutting down API')

    app.include_router(api_router)
    return app


app = create_app()
