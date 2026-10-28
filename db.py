"""Database layer: stores the user's progress for each NSM principle in SQLite.

The NSM principles themselves live in nsm_data.py (they never change at runtime).
This file only stores what the user adds: status, notes, ISO reference, GDPR flag.
"""

import sqlite3
from pathlib import Path

# The database file sits next to this script. It is created on first run.
DB_PATH = Path(__file__).parent / "grunnmur.db"

# The three allowed statuses. The key is stored in the database,
# the value is the Norwegian label shown in the interface.
STATUSES = {
    "ikke_startet": "Ikke startet",
    "delvis": "Delvis",
    "implementert": "Implementert",
}


def connect():
    """Open a connection where rows behave like dictionaries (row["status"])."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the table if it does not exist yet. Safe to run on every start."""
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                principle_id TEXT PRIMARY KEY,           -- e.g. "2.6"
                status       TEXT NOT NULL DEFAULT 'ikke_startet',
                notes        TEXT NOT NULL DEFAULT '',   -- evidence / comments
                iso_ref      TEXT NOT NULL DEFAULT '',   -- e.g. "A.5.15, A.8.5"
                gdpr         INTEGER NOT NULL DEFAULT 0  -- 1 = personvern-relevant
            )
            """
        )


def get_all_progress():
    """Return {principle_id: row} for every principle the user has saved."""
    with connect() as conn:
        rows = conn.execute("SELECT * FROM progress").fetchall()
    return {row["principle_id"]: row for row in rows}


def save_progress(principle_id, status, notes, iso_ref, gdpr):
    """Insert or update one principle (an "upsert").

    The ? placeholders let sqlite3 escape the values, which protects
    against SQL injection.
    """
    if status not in STATUSES:
        status = "ikke_startet"
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO progress (principle_id, status, notes, iso_ref, gdpr)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(principle_id) DO UPDATE SET
                status = excluded.status,
                notes = excluded.notes,
                iso_ref = excluded.iso_ref,
                gdpr = excluded.gdpr
            """,
            (principle_id, status, notes.strip(), iso_ref.strip(), 1 if gdpr else 0),
        )
