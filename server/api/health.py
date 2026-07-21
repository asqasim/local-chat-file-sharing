"""
Health check endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter
from datetime import datetime, UTC

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health() -> dict:
    """Return server health information."""

    return {
        "status": "online",
        "server": "Local Chat File Sharing",
        "version": "0.1.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }