"""
Application entry point.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from server.config import create_directories, settings
from server.database import database


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    create_directories()
    database.initialize()

    app = FastAPI(
        title="Local Chat File Sharing",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
    )

    client_directory = Path(settings.CLIENT_DIR)

    if client_directory.exists():
        app.mount(
            "/",
            StaticFiles(directory=client_directory, html=True),
            name="client",
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )