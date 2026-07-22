"""
Pairing API
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from server.database import database
from server.websocket import manager

router = APIRouter(
    prefix="/api/pairing",
    tags=["Pairing"],
)


PAIRING_DURATION = 300  # 5 minutes


class PairRequest(BaseModel):

    code: str

    device_id: str

    device_name: str

    platform: str

    ip_address: str


# ==========================================================
# Generate Pairing Code
# ==========================================================

@router.post("/generate")
async def generate_pairing_code():

    code = f"{random.randint(100000, 999999)}"

    created_at = datetime.now(UTC)

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
            VALUES (?, ?, ?, ?)
            """,
            (
                code,
                created_at.isoformat(),
                expires_at.isoformat(),
                0,
            ),
        )

    return {
        "code": code,
        "expires_in": PAIRING_DURATION,
    }


# ==========================================================
# Verify Pairing Code
# ==========================================================

@router.post("/verify")
async def verify_pairing(
    request: PairRequest,
):

    now = datetime.now(UTC)

    with database.connection() as connection:

        session = connection.execute(
            """
            SELECT
                code,
                expires_at
            FROM pairing_sessions
            WHERE code = ?
            """,
            (request.code,),
        ).fetchone()

        if session is None:

            raise HTTPException(
                status_code=404,
                detail="Invalid pairing code.",
            )

        expires = datetime.fromisoformat(
            session["expires_at"]
        )

        if now > expires:

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
                request.device_name,
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
            (request.code,),
        )

    payload = {
        "device_id": request.device_id,
        "name": request.device_name,
        "platform": request.platform,
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
    }


# ==========================================================
# Pairing Status
# ==========================================================

@router.get("/status")
async def pairing_status():

    with database.connection() as connection:

        session = connection.execute(
            """
            SELECT
                code,
                expires_at,
                verified
            FROM pairing_sessions
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()

    if session is None:

        return {
            "active": False
        }

    return {
        "active": True,
        "code": session["code"],
        "expires_at": session["expires_at"],
        "verified": bool(session["verified"]),
    }