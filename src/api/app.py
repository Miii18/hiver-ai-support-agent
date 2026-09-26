from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import settings
from src.api.routes import router as api_router

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

LOGGER = logging.getLogger("api.app")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup event
    @app.on_event("startup")
    async def startup_event() -> None:
        LOGGER.info(
            "Starting %s v%s",
            settings.project_name,
            settings.version,
        )
        LOGGER.info(
            "API started successfully. Chatbot will load on first request."
        )

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        LOGGER.info("Shutting down API")

    # Register routes
    app.include_router(api_router)

    return app


app = create_app()