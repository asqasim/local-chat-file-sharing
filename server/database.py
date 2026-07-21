"""
SQLite database management.

This module owns the application's SQLite connection and schema creation.
Other modules should interact with the database only through this layer.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from config import settings


class Database:
    """SQLite database manager."""

    def __init__(self, database_file: Path) -> None:
        self._database_file = database_file

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a configured SQLite connection."""

        connection = sqlite3.connect(self._database_file)
        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON;")
        connection.execute("PRAGMA journal_mode = WAL;")

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        """Create all required tables."""

        with self.connection() as connection:
            cursor = connection.cursor()

            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    last_ip TEXT,
                    paired_at TEXT NOT NULL,
                    last_seen TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(sender_id)
                        REFERENCES devices(id),

                    FOREIGN KEY(receiver_id)
                        REFERENCES devices(id)
                );

                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    message_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    stored_name TEXT NOT NULL,
                    mime_type TEXT,
                    file_size INTEGER NOT NULL,
                    checksum TEXT,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(message_id)
                        REFERENCES messages(id)
                        ON DELETE CASCADE
                );
                """
            )


database = Database(settings.DATABASE_FILE)