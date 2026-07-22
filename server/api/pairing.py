"""
Pairing API
"""

from __future__ import annotations

import random
from datetime import UTC
from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field

from server.database import database
from server.websocket import manager

router = APIRouter(
    prefix="/api/pairing",
    tags=["Pairing"],
)

PAIRING_DURATION = 300


# ==========================================================
# Models
# ==========================================================

class PairDeviceRequest(BaseModel):

    code: str = Field(
        min_length=6,
        max_length=6,
    )

    device_id: str

    name: str

    platform: str

    ip_address: str


# ==========================================================
# Generate Pairing Code
# ==========================================================

@router.post("/generate")
async def generate_pairing_code():

    code = str(
        random.randint(
            100000,
            999999,
        )
    )

    created_at = datetime.now(
        UTC
    )

    expires_at = created_at + timedelta(
        seconds=PAIRING_DURATION
    )

    with database.connection() as connection:

        connection.execute(
            "DELETE FROM pairing_sessions"
        )

        connection.execute(
            """
            INSERT INTO pairing_sessions
            (
                code,
                created_at,
                expires_at,
                verified
            )
            VALUES
            (?, ?, ?, ?)
            """,
            (
                code,
                created_at.isoformat(),
                expires_at.isoformat(),
                0,
            ),
        )

    return {
        "success": True,
        "data": {
            "code": code,
            "expires_in": PAIRING_DURATION,
        },
    }


# ==========================================================
# Pair Device
# ==========================================================

@router.post("/verify")
async def verify_pairing(
    request: PairDeviceRequest,
):

    now = datetime.now(
        UTC
    )

    with database.connection() as connection:

        session = connection.execute(
            """
            SELECT
                code,
                expires_at,
                verified
            FROM pairing_sessions
            WHERE code = ?
            """,
            (
                request.code,
            ),
        ).fetchone()

        if session is None:

            raise HTTPException(
                status_code=404,
                detail="Invalid pairing code.",
            )

        expires_at = datetime.fromisoformat(
            session["expires_at"]
        )

        if now > expires_at:

            raise HTTPException(
                status_code=400,
                detail="Pairing code expired.",
            )

        connection.execute(
            """
            INSERT OR REPLACE INTO devices
            (
                device_id,
                name,
                platform,
                ip_address,
                online,
                paired,
                last_seen
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.device_id,
                request.name,
                request.platform,
                request.ip_address,
                1,
                1,
                now.isoformat(),
            ),
        )

        connection.execute(
            """
            UPDATE pairing_sessions
            SET verified = 1
            WHERE code = ?
            """,
            (
                request.code,
            ),
        )

    payload = {

        "device_id": request.device_id,

        "name": request.name,

        "platform": request.platform,

        "ip_address": request.ip_address,

        "paired": True,

        "online": True,

    }

    await manager.broadcast(
        {
            "type": "device_paired",
            "device": payload,
        }
    )

    return {
        "success": True,
        "message": "Device paired successfully.",
        "data": payload,
    }


# ==========================================================
# Pairing Status
# ==========================================================

@router.get("/status")
async def pairing_status():

    now = datetime.now(
        UTC
    )

    with database.connection() as connection:

        session = connection.execute(
            """
            SELECT
                code,
                created_at,
                expires_at,
                verified
            FROM pairing_sessions
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()

    if session is None:

        return {
            "success": True,
            "data": {
                "active": False,
            },
        }

    expires_at = datetime.fromisoformat(
        session["expires_at"]
    )

    active = now <= expires_at

    return {
        "success": True,
        "data": {

            "active": active,

            "code": session["code"],

            "created_at": session["created_at"],

            "expires_at": session["expires_at"],

            "verified": bool(
                session["verified"]
            ),

        },
    }


# ==========================================================
# Cancel Pairing Session
# ==========================================================

@router.delete("/session")
async def cancel_pairing_session():

    with database.connection() as connection:

        connection.execute(
            """
            DELETE FROM pairing_sessions
            """
        )

    await manager.broadcast(
        {
            "type": "pairing_cancelled",
        }
    )

    return {
        "success": True,
        "message": "Pairing session cancelled.",
    }


# ==========================================================
# Unpair Device
# ==========================================================

@router.delete("/{device_id}")
async def unpair_device(
    device_id: str,
):

    with database.connection() as connection:

        cursor = connection.execute(
            """
            UPDATE devices
            SET
                paired = 0,
                online = 0
            WHERE device_id = ?
            """,
            (
                device_id,
            ),
        )

    if cursor.rowcount == 0:

        raise HTTPException(
            status_code=404,
            detail="Device not found.",
        )

    await manager.broadcast(
        {
            "type": "device_unpaired",
            "device_id": device_id,
        }
    )

    return {
        "success": True,
        "message": "Device unpaired.",
    }


# ==========================================================
# Cleanup Expired Sessions
# ==========================================================

@router.delete("/expired")
async def cleanup_expired_sessions():

    now = datetime.now(
        UTC
    ).isoformat()

    with database.connection() as connection:

        cursor = connection.execute(
            """
            DELETE
            FROM pairing_sessions
            WHERE expires_at < ?
            """,
            (
                now,
            ),
        )

    return {
        "success": True,
        "message": "Expired sessions removed.",
        "data": {
            "deleted": cursor.rowcount,
        },
    }