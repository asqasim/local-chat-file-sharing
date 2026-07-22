"""
Devices API
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field

from server.database import database
from server.websocket import manager

router = APIRouter(
    prefix="/api/devices",
    tags=["Devices"],
)


# ==========================================================
# Models
# ==========================================================

class DeviceRegister(BaseModel):

    device_id: str = Field(
        min_length=3,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    platform: str = Field(
        min_length=1,
        max_length=50,
    )

    ip_address: str


class DeviceStatus(BaseModel):

    online: bool


# ==========================================================
# Register / Update Device
# ==========================================================

@router.post("")
async def register_device(
    device: DeviceRegister,
):

    now = datetime.now(
        UTC
    ).isoformat()

    with database.connection() as connection:

        existing = connection.execute(
            """
            SELECT device_id
            FROM devices
            WHERE device_id = ?
            """,
            (
                device.device_id,
            ),
        ).fetchone()

        if existing:

            connection.execute(
                """
                UPDATE devices
                SET

                    name = ?,

                    platform = ?,

                    ip_address = ?,

                    online = 1,

                    paired = 1,

                    last_seen = ?

                WHERE device_id = ?
                """,
                (
                    device.name,
                    device.platform,
                    device.ip_address,
                    now,
                    device.device_id,
                ),
            )

        else:

            connection.execute(
                """
                INSERT INTO devices
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
                    device.device_id,
                    device.name,
                    device.platform,
                    device.ip_address,
                    1,
                    1,
                    now,
                ),
            )

    payload = {

        "device_id": device.device_id,

        "name": device.name,

        "platform": device.platform,

        "ip_address": device.ip_address,

        "online": True,

        "paired": True,

        "last_seen": now,

    }

    await manager.broadcast(
        {
            "type": "device_updated",
            "device": payload,
        }
    )

    return {
        "success": True,
        "message": "Device registered.",
        "data": payload,
    }


# ==========================================================
# List Devices
# ==========================================================

@router.get("")
async def list_devices():

    with database.connection() as connection:

        rows = connection.execute(
            """
            SELECT

                device_id,

                name,

                platform,

                ip_address,

                online,

                paired,

                last_seen

            FROM devices

            ORDER BY name
            """
        ).fetchall()

    return {

        "success": True,

        "data": [

            dict(row)

            for row in rows

        ]

    }


# ==========================================================
# Get Device
# ==========================================================

@router.get("/{device_id}")
async def get_device(
    device_id: str,
):

    with database.connection() as connection:

        row = connection.execute(
            """
            SELECT
                device_id,
                name,
                platform,
                ip_address,
                online,
                paired,
                last_seen
            FROM devices
            WHERE device_id = ?
            """,
            (
                device_id,
            ),
        ).fetchone()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Device not found.",
        )

    return {

        "success": True,

        "data": dict(row),

    }