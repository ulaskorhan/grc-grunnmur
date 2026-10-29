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
        # v2: the risk register. The score is not stored; it is always
        # calculated as likelihood × impact (see risks.py).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS risks (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                description  TEXT NOT NULL DEFAULT '',
                likelihood   INTEGER NOT NULL,          -- 1-5
                impact       INTEGER NOT NULL,          -- 1-5
                treatment    TEXT NOT NULL,             -- redusere / akseptere / unnga / overfore
                actions      TEXT NOT NULL DEFAULT '',  -- what is done about it
                principle_id TEXT NOT NULL DEFAULT '',  -- linked NSM principle, e.g. "2.9"
                status       TEXT NOT NULL DEFAULT 'apen',
                review_date  TEXT NOT NULL DEFAULT '',  -- YYYY-MM-DD, or empty
                gdpr         INTEGER NOT NULL DEFAULT 0
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


# ---------- v2: risk register ----------

# The columns a risk form fills in (everything except the id).
# The SQL below builds column names from this fixed list with f-strings. That is
# safe because the names come from this code, never from the user. All values
# still go through ? placeholders, which protects against SQL injection.
RISK_FIELDS = ["title", "description", "likelihood", "impact", "treatment",
               "actions", "principle_id", "status", "review_date", "gdpr"]


def get_all_risks():
    """Return every risk as a list of dictionaries."""
    with connect() as conn:
        rows = conn.execute("SELECT * FROM risks").fetchall()
    return [dict(row) for row in rows]


def get_risk(risk_id):
    """Return one risk as a dictionary, or None if it does not exist."""
    with connect() as conn:
        row = conn.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()
    return dict(row) if row else None


def add_risk(data):
    """Insert a new risk. data is the dictionary from risks.read_form()."""
    columns = ", ".join(RISK_FIELDS)
    placeholders = ", ".join("?" for _ in RISK_FIELDS)
    with connect() as conn:
        conn.execute(f"INSERT INTO risks ({columns}) VALUES ({placeholders})",
                     [data[field] for field in RISK_FIELDS])


def update_risk(risk_id, data):
    """Overwrite an existing risk with new values."""
    assignments = ", ".join(f"{field} = ?" for field in RISK_FIELDS)
    with connect() as conn:
        conn.execute(f"UPDATE risks SET {assignments} WHERE id = ?",
                     [data[field] for field in RISK_FIELDS] + [risk_id])


def delete_risk(risk_id):
    with connect() as conn:
        conn.execute("DELETE FROM risks WHERE id = ?", (risk_id,))
