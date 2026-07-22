"""
Messages API
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.database import database
from server.websocket import manager

router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"],
)


class MessageCreate(BaseModel):

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
async def create_message(
    message: MessageCreate,
):

    text = message.content.strip()

    if not text:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    payload = {

        "id": str(uuid.uuid4()),

        "sender_id": message.sender_id,

        "receiver_id": message.receiver_id,

        "message_type": "text",

        "content": text,

        "status": "sent",

        "created_at": datetime.now(
            UTC
        ).isoformat(),

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
            VALUES
            (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["id"],
                payload["sender_id"],
                payload["receiver_id"],
                payload["message_type"],
                payload["content"],
                payload["status"],
                payload["created_at"],
            ),
        )

    await manager.broadcast(
        {
            "type": "message_created",
            "message": payload,
        }
    )

    return payload


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
):

    with database.connection() as connection:

        cursor = connection.execute(
            """
            DELETE
            FROM messages
            WHERE id = ?
            """,
            (message_id,),
        )

    if cursor.rowcount == 0:

        raise HTTPException(
            status_code=404,
            detail="Message not found.",
        )

    await manager.broadcast(
        {
            "type": "message_deleted",
            "id": message_id,
        }
    )

    return {
        "success": True
    }