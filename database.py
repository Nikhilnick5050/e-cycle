"""
E-Cycle — database setup and helper functions.

Creates the SQLite database and tables automatically on first launch.
All queries use parameterised statements to prevent SQL injection.
"""

import os
import sqlite3

# The database file lives next to this script by default.
# On Render, set DB_PATH to the persistent disk (e.g. /var/data/ecycle.db).
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecycle.db"))


def get_db():
    """Open a connection to the SQLite database (rows as dict-like objects)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the tables if they do not already exist."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS e_waste_requests (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id      TEXT UNIQUE NOT NULL,
            submitted_at    TEXT NOT NULL,
            full_name       TEXT NOT NULL,
            contact         TEXT NOT NULL,
            pickup_location TEXT NOT NULL,
            item_type       TEXT NOT NULL,
            condition       TEXT NOT NULL,
            quantity        INTEGER NOT NULL,
            notes           TEXT,
            category        TEXT NOT NULL,
            recommendation  TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'Pending'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()