"""
SQLite Database Manager
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


DATABASE_DIR = Path(__file__).parent / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "localshare.db"


class Database:

    def __init__(self) -> None:

        self.initialize()

    # ==========================================================
    # Connection
    # ==========================================================

    @contextmanager
    def connection(self):

        connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
        )

        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON;")
        connection.execute("PRAGMA journal_mode = WAL;")
        connection.execute("PRAGMA synchronous = NORMAL;")

        try:

            yield connection

            connection.commit()

        except Exception:

            connection.rollback()

            raise

        finally:

            connection.close()

    # ==========================================================
    # Initialize
    # ==========================================================

    def initialize(self) -> None:

        with self.connection() as connection:

            self.create_messages_table(connection)

            self.create_files_table(connection)

            self.create_devices_table(connection)

            self.create_pairing_table(connection)

    # ==========================================================
    # Messages
    # ==========================================================

    def create_messages_table(
        self,
        connection: sqlite3.Connection,
    ):

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (

                id TEXT PRIMARY KEY,

                sender_id TEXT NOT NULL,

                receiver_id TEXT NOT NULL,

                message_type TEXT NOT NULL,

                content TEXT,

                file_id TEXT,

                status TEXT NOT NULL,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_created
            ON messages(created_at)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_sender
            ON messages(sender_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_receiver
            ON messages(receiver_id)
            """
        )

    # ==========================================================
    # Files
    # ==========================================================

    def create_files_table(
        self,
        connection: sqlite3.Connection,
    ):

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS files (

                id TEXT PRIMARY KEY,

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
            idx_files_created
            ON files(created_at)
            """
        )

    # ==========================================================
    # Devices
    # ==========================================================

    def create_devices_table(
        self,
        connection: sqlite3.Connection,
    ):

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (

                device_id TEXT PRIMARY KEY,

                name TEXT NOT NULL,

                platform TEXT NOT NULL,

                ip_address TEXT,

                online INTEGER NOT NULL DEFAULT 0,

                paired INTEGER NOT NULL DEFAULT 0,

                last_seen TEXT NOT NULL

            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_devices_online
            ON devices(online)
            """
        )

    # ==========================================================
    # Pairing Sessions
    # ==========================================================

    def create_pairing_table(
        self,
        connection: sqlite3.Connection,
    ):

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pairing_sessions (

                code TEXT PRIMARY KEY,

                created_at TEXT NOT NULL,

                expires_at TEXT NOT NULL,

                verified INTEGER NOT NULL DEFAULT 0

            )
            """
        )


database = Database()