"""
Application data models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Message:
    id: str
    sender_id: str
    receiver_id: str
    message_type: str
    content: str
    status: str
    created_at: str