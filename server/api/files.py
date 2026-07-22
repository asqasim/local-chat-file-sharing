"""
Files API
"""

from __future__ import annotations

import mimetypes
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile

from server.database import database
from server.websocket import manager

router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)

# ==========================================================
# Storage
# ==========================================================

STORAGE_DIR = Path("storage")

IMAGE_TYPES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".webp",
}

VIDEO_TYPES = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".webm",
}

DOCUMENT_TYPES = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
    ".csv",
}

AUDIO_TYPES = {
    ".mp3",
    ".wav",
    ".aac",
    ".ogg",
    ".flac",
}

ARCHIVE_TYPES = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
}


def get_category(extension: str) -> str:

    extension = extension.lower()

    if extension in IMAGE_TYPES:
        return "images"

    if extension in VIDEO_TYPES:
        return "videos"

    if extension in DOCUMENT_TYPES:
        return "documents"

    if extension in AUDIO_TYPES:
        return "audio"

    if extension in ARCHIVE_TYPES:
        return "archives"

    return "others"


# ==========================================================
# Upload
# ==========================================================

@router.post("")
async def upload_file(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    extension = Path(file.filename).suffix

    category = get_category(extension)

    file_id = str(uuid.uuid4())

    stored_name = f"{file_id}{extension}"

    folder = STORAGE_DIR / category

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = folder / stored_name

    with destination.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    file_size = destination.stat().st_size

    mime_type, _ = mimetypes.guess_type(
        destination
    )

    payload = {

        "id": file_id,

        "file_name": file.filename,

        "stored_name": stored_name,

        "category": category,

        "size": file_size,

        "mime_type": mime_type,

        "created_at": datetime.now(
            UTC
        ).isoformat(),

    }

    with database.connection() as connection:

        connection.execute(
            """
            INSERT INTO files
            (
                id,
                file_name,
                stored_name,
                category,
                mime_type,
                file_size,
                created_at
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["id"],
                payload["file_name"],
                payload["stored_name"],
                payload["category"],
                payload["mime_type"],
                payload["size"],
                payload["created_at"],
            ),
        )

    await manager.broadcast(
        {
            "type": "file_uploaded",
            "file": payload,
        }
    )

    return payload