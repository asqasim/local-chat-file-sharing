"""
Devices API
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from server.database import database
from server.websocket import manager

router = APIRouter(
    prefix="/api/devices",
    tags=["Devices"],
)


# ==========================================================
# Models
# ==========================================================

class DeviceCreate(BaseModel):

    device_id: str

    name: str

    platform: str

    ip_address: str


class DeviceStatus(BaseModel):

    online: bool


# ==========================================================
# Register Device
# ==========================================================

@router.post("")
async def register_device(
    device: DeviceCreate,
):

    now = datetime.now(
        UTC
    ).isoformat()

    with database.connection() as connection:

        existing = connection.execute(
            """
            SELECT id
            FROM devices
            WHERE id = ?
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
                    last_seen = ?
                WHERE id = ?
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
                    id,
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

        "id": device.device_id,

        "name": device.name,

        "platform": device.platform,

        "ip_address": device.ip_address,

        "online": True,

        "last_seen": now,

    }

    await manager.broadcast(
        {
            "type": "device_updated",
            "device": payload,
        }
    )

    return payload


# ==========================================================
# List Devices
# ==========================================================

@router.get("")
async def list_devices():

    with database.connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
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

    return [
        dict(row)
        for row in rows
    ]


# ==========================================================
# Update Status
# ==========================================================

@router.put("/{device_id}/status")
async def update_status(
    device_id: str,
    status: DeviceStatus,
):

    now = datetime.now(
        UTC
    ).isoformat()

    with database.connection() as connection:

        cursor = connection.execute(
            """
            UPDATE devices
            SET
                online = ?,
                last_seen = ?
            WHERE id = ?
            """,
            (
                int(status.online),
                now,
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
            "type": "device_status",
            "device_id": device_id,
            "online": status.online,
        }
    )

    return {
        "success": True,
    }


# ==========================================================
# Delete Device
# ==========================================================

@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
):

    with database.connection() as connection:

        cursor = connection.execute(
            """
            DELETE
            FROM devices
            WHERE id = ?
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
            "type": "device_removed",
            "device_id": device_id,
        }
    )

    return {
        "success": True,
    }