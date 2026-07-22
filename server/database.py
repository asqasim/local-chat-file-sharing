"""
SQLite Database Manager
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:

    def __init__(self) -> None:

        self.database_dir = Path(__file__).parent / "database"

        self.database_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.database_path = (
            self.database_dir / "localshare.db"
        )

        self.initialize()

    # ==========================================================
    # Connection
    # ==========================================================

    def connection(self) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON;"
        )

        connection.execute(
            "PRAGMA journal_mode = WAL;"
        )

        connection.execute(
            "PRAGMA synchronous = NORMAL;"
        )

        return connection

    # ==========================================================
    # Initialize
    # ==========================================================

    def initialize(self) -> None:

        with self.connection() as connection:

            self.create_messages_table(
                connection
            )

            self.create_files_table(
                connection
            )

    # ==========================================================
    # Messages
    # ==========================================================

    def create_messages_table(
        self,
        connection: sqlite3.Connection,
    ) -> None:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id TEXT NOT NULL,

                receiver_id TEXT NOT NULL,

                message_type TEXT NOT NULL,

                content TEXT,

                file_id INTEGER,

                status TEXT NOT NULL,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_created_at

            ON messages(created_at)
            """
        )

    # ==========================================================
    # Files
    # ==========================================================

    def create_files_table(
        self,
        connection: sqlite3.Connection,
    ) -> None:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS files (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                uuid TEXT UNIQUE NOT NULL,

                file_name TEXT NOT NULL,

                stored_name TEXT NOT NULL,

                category TEXT NOT NULL,

                mime_type TEXT,

                file_size INTEGER NOT NULL,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_files_category

            ON files(category)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_files_created_at

            ON files(created_at)
            """
        )