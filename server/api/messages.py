"""
Text message API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from server.database import database


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
                content,
                created_at
            FROM messages
            ORDER BY created_at ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


@router.post("")
async def create_message(request: CreateMessageRequest):

    message_id = str(uuid.uuid4())

    created_at = datetime.now(UTC).isoformat()

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
                message_id,
                request.sender_id,
                request.receiver_id,
                "text",
                request.content,
                "sent",
                created_at,
            ),
        )

    return {
        "success": True,
        "id": message_id,
    }