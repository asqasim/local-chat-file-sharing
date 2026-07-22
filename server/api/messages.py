"""
Messages API
"""

from __future__ import annotations

import uuid
from datetime import UTC
from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field

from server.database import database
from server.websocket import manager

router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"],
)


# ==========================================================
# Models
# ==========================================================

class MessageCreate(BaseModel):

    sender_id: str

    receiver_id: str

    content: str = Field(
        min_length=1,
        max_length=5000,
    )

    message_type: str = "text"

    file_id: str | None = None


# ==========================================================
# Helpers
# ==========================================================

VALID_MESSAGE_TYPES = {
    "text",
    "image",
    "video",
    "audio",
    "document",
    "archive",
}


def build_message_payload(
    message: MessageCreate,
):

    return {

        "id": str(uuid.uuid4()),

        "sender_id": message.sender_id,

        "receiver_id": message.receiver_id,

        "message_type": message.message_type,

        "content": message.content.strip(),

        "file_id": message.file_id,

        "status": "sent",

        "created_at": datetime.now(
            UTC
        ).isoformat(),

    }


# ==========================================================
# List Messages
# ==========================================================

@router.get("")
async def list_messages():

    with database.connection() as connection:

        rows = connection.execute(
            """
            SELECT

                id,

                sender_id,

                receiver_id,

                message_type,

                content,

                file_id,

                status,

                created_at

            FROM messages

            ORDER BY created_at ASC
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
# Send Message
# ==========================================================

@router.post("")
async def send_message(
    message: MessageCreate,
):

    if message.message_type not in VALID_MESSAGE_TYPES:

        raise HTTPException(

            status_code=400,

            detail="Invalid message type.",

        )

    payload = build_message_payload(
        message
    )

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
                file_id,
                status,
                created_at
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["id"],
                payload["sender_id"],
                payload["receiver_id"],
                payload["message_type"],
                payload["content"],
                payload["file_id"],
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

    return {

        "success": True,

        "message": "Message sent.",

        "data": payload,

    }