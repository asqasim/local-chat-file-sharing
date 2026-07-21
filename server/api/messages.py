"""
Message API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from server.database import database
from server.websocket import manager


router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"],
)


class CreateMessageRequest(BaseModel):
    sender_id: str
    receiver_id: str
    content: str


@router.get("")
async def get_messages():

    with database.connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                sender_id,
                receiver_id,
                receiver_id,
                message_type,
                content,
                status,
                created_at
            FROM messages
            ORDER BY created_at ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


@router.post("")
async def create_message(request: CreateMessageRequest):

    message = {
        "id": str(uuid.uuid4()),
        "sender_id": request.sender_id,
        "receiver_id": request.receiver_id,
        "message_type": "text",
        "content": request.content,
        "status": "sent",
        "created_at": datetime.now(UTC).isoformat(),
    }

    with database.connection() as connection:

        connection.execute(
            """
            INSERT INTO messages
            (
                id,
                sender_id,
                receiver_id,
                message_type,
                content,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message["id"],
                message["sender_id"],
                message["receiver_id"],
                message["message_type"],
                message["content"],
                message["status"],
                message["created_at"],
            ),
        )

    await manager.broadcast(
        {
            "type": "new_message",
            "message": message,
        }
    )

    return message