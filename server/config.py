"""
Application configuration.

All project-wide configuration lives here.
No other module should hardcode paths, ports, or timing values.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application settings."""

    # ------------------------------------------------------------------
    # Project Paths
    # ------------------------------------------------------------------

    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    SERVER_DIR: Path = PROJECT_ROOT / "server"
    CLIENT_DIR: Path = PROJECT_ROOT / "client"

    DATABASE_DIR: Path = SERVER_DIR / "database"
    DATABASE_FILE: Path = DATABASE_DIR / "localshare.db"

    UPLOADS_DIR: Path = SERVER_DIR / "uploads"
    THUMBNAILS_DIR: Path = SERVER_DIR / "thumbnails"

    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # ------------------------------------------------------------------
    # HTTP Server
    # ------------------------------------------------------------------

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ------------------------------------------------------------------
    # Device
    # ------------------------------------------------------------------

    DEVICE_NAME: str = "SHOP-PC"

    # ------------------------------------------------------------------
    # UDP Discovery
    # ------------------------------------------------------------------

    DISCOVERY_PORT: int = 50505
    DISCOVERY_MESSAGE: str = "LOCALSHARE_ONLINE"
    BROADCAST_INTERVAL: int = 2
    BROADCAST_RETRIES: int = 5

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    MAX_UPLOAD_SIZE_MB: int = 1024
    CHUNK_SIZE: int = 1024 * 1024  # 1 MB

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = LOGS_DIR / "server.log"


settings = Settings()


def create_directories() -> None:
    """Create required project directories if they do not exist."""

    directories = (
        settings.DATABASE_DIR,
        settings.UPLOADS_DIR,
        settings.THUMBNAILS_DIR,
        settings.LOGS_DIR,
    )

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)