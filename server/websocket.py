"""
WebSocket Manager
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC
from datetime import datetime

from fastapi import WebSocket
from fastapi import WebSocketDisconnect


class ConnectionManager:

    def __init__(self):

        self.connections: dict[str, WebSocket] = {}

        self.last_seen: dict[str, str] = {}

    # ==========================================================
    # Connect
    # ==========================================================

    async def connect(
        self,
        websocket: WebSocket,
        device_id: str,
    ):

        await websocket.accept()

        self.connections[
            device_id
        ] = websocket

        self.last_seen[
            device_id
        ] = datetime.now(
            UTC
        ).isoformat()

        await self.broadcast(
            {
                "type": "device_connected",
                "device_id": device_id,
            }
        )

    # ==========================================================
    # Disconnect
    # ==========================================================

    async def disconnect(
        self,
        device_id: str,
    ):

        self.connections.pop(
            device_id,
            None,
        )

        self.last_seen[
            device_id
        ] = datetime.now(
            UTC
        ).isoformat()

        await self.broadcast(
            {
                "type": "device_disconnected",
                "device_id": device_id,
            }
        )

    # ==========================================================
    # Send
    # ==========================================================

    async def send(
        self,
        device_id: str,
        payload: dict,
    ):

        websocket = self.connections.get(
            device_id
        )

        if websocket is None:

            return False

        try:

            await websocket.send_json(
                payload
            )

            return True

        except Exception:

            await self.disconnect(
                device_id
            )

            return False

    # ==========================================================
    # Broadcast
    # ==========================================================

    async def broadcast(
        self,
        payload: dict,
    ):

        disconnected = []

        for (
            device_id,
            websocket,
        ) in self.connections.items():

            try:

                await websocket.send_json(
                    payload
                )

            except Exception:

                disconnected.append(
                    device_id
                )

        for device_id in disconnected:

            await self.disconnect(
                device_id
            )

    # ==========================================================
    # Receive Loop
    # ==========================================================

    async def listen(
        self,
        websocket: WebSocket,
        device_id: str,
    ):

        try:

            while True:

                data = await websocket.receive_text()

                self.last_seen[
                    device_id
                ] = datetime.now(
                    UTC
                ).isoformat()

                try:

                    payload = json.loads(
                        data
                    )

                except Exception:

                    continue

                payload.setdefault(
                    "device_id",
                    device_id,
                )

                await self.broadcast(
                    payload
                )

        except WebSocketDisconnect:

            await self.disconnect(
                device_id
            )