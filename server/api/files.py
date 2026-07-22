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

PROJECT_ROOT = Path(__file__).resolve().parents[2]

STORAGE_DIR = PROJECT_ROOT / "storage"

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".webp",
    ".svg",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".m4v",
}

DOCUMENT_EXTENSIONS = {
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

AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".aac",
    ".ogg",
    ".flac",
    ".m4a",
}

ARCHIVE_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
}


def get_category(extension: str) -> str:

    extension = extension.lower()

    if extension in IMAGE_EXTENSIONS:
        return "images"

    if extension in VIDEO_EXTENSIONS:
        return "videos"

    if extension in DOCUMENT_EXTENSIONS:
        return "documents"

    if extension in AUDIO_EXTENSIONS:
        return "audio"

    if extension in ARCHIVE_EXTENSIONS:
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

    extension = Path(
        file.filename
    ).suffix.lower()

    category = get_category(
        extension
    )

    file_id = str(
        uuid.uuid4()
    )

    stored_name = (
        f"{file_id}{extension}"
    )

    destination_folder = (
        STORAGE_DIR / category
    )

    destination_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        destination_folder / stored_name
    )

    with destination.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    mime_type, _ = mimetypes.guess_type(
        destination
    )

    payload = {

        "id": file_id,

        "file_name": file.filename,

        "stored_name": stored_name,

        "category": category,

        "mime_type": mime_type
        or "application/octet-stream",

        "file_size": destination.stat().st_size,

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
                payload["file_size"],
                payload["created_at"],
            ),
        )

    await manager.broadcast(
        {
            "type": "file_uploaded",
            "file": payload,
        }
    )

    return {
        "success": True,
        "message": "File uploaded.",
        "data": payload,
    }