"""
Message repository.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from server.database import database
from server.models import Message


class MessageRepository:

    def create(
        self,
        sender_id: str,
        receiver_id: str,
        content: str,
    ) -> Message:

        message = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type="text",
            content=content,
            status="sent",
            created_at=datetime.now(UTC).isoformat(),
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
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.id,
                    message.sender_id,
                    message.receiver_id,
                    message.message_type,
                    message.content,
                    message.status,
                    message.created_at,
                ),
            )

        return message

    def all(self) -> list[Message]:

        with database.connection() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM messages
                ORDER BY created_at
                """
            ).fetchall()

        return [
            Message(
                **dict(row),
            )
            for row in rows
        ]


message_repository = MessageRepository()