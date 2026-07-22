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

    # ==========================================================
# Broadcast Except Sender
# ==========================================================

    async def broadcast_except(
        self,
        sender_id: str,
        payload: dict,
    ):

        disconnected = []

        for device_id, websocket in self.connections.items():

            if device_id == sender_id:
                continue

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
                device_id,
            )

    # ==========================================================
    # Heartbeat
    # ==========================================================

    async def heartbeat(
        self,
        device_id: str,
    ):

        websocket = self.connections.get(
            device_id
        )

        if websocket is None:

            return False

        try:

            await websocket.send_json(
                {
                    "type": "ping",
                    "timestamp": datetime.now(
                        UTC
                    ).isoformat(),
                }
            )

            self.last_seen[
                device_id
            ] = datetime.now(
                UTC
            ).isoformat()

            return True

        except Exception:

            await self.disconnect(
                device_id,
            )

            return False

    async def heartbeat_loop(
        self,
        interval: int = 30,
    ):

        while True:

            await asyncio.sleep(
                interval
            )

            for device_id in list(
                self.connections.keys()
            ):

                await self.heartbeat(
                    device_id
                )

    # ==========================================================
    # Helpers
    # ==========================================================

    def is_connected(
        self,
        device_id: str,
    ) -> bool:

        return (
            device_id
            in self.connections
        )

    def connection_count(
        self,
    ) -> int:

        return len(
            self.connections
        )

    def connected_devices(
        self,
    ) -> list[str]:

        return sorted(
            self.connections.keys()
        )

    def last_seen_time(
        self,
        device_id: str,
    ) -> str | None:

        return self.last_seen.get(
            device_id
        )

    async def shutdown(self):

        for websocket in list(
            self.connections.values()
        ):

            try:

                await websocket.close()

            except Exception:

                pass

        self.connections.clear()

        self.last_seen.clear()


# ==========================================================
# Singleton
# ==========================================================

manager = ConnectionManager()