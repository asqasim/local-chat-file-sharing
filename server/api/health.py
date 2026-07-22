"""
Health API
"""

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/health",
    tags=["Health"],
)

SERVER_STARTED = datetime.now(UTC)


@router.get("")
async def health():

    now = datetime.now(UTC)

    uptime = int(
        (now - SERVER_STARTED).total_seconds()
    )

    return {
        "status": "online",
        "service": "LocalShare",
        "version": "0.1.0",
        "server_time": now.isoformat(),
        "uptime_seconds": uptime,
    }