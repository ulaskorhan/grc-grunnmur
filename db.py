"""Database layer: stores the user's progress for each NSM principle in SQLite.

The NSM principles themselves live in nsm_data.py (they never change at runtime).
This file only stores what the user adds: status, notes, ISO reference, GDPR flag,
the risk register (v2), ISO 27001 clause status and the statement of applicability (v4),
and the status of NSM's measures (v5). import_all() saves an imported file (v7).
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
        # v4: status per ISO 27001 requirement (clauses 4-10), e.g. "6.1.2"
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS isms (
                item_id TEXT PRIMARY KEY,
                status  TEXT NOT NULL DEFAULT 'ikke_startet',
                notes   TEXT NOT NULL DEFAULT ''
            )
            """
        )
        # v4: statement of applicability (SoA): does each ISO 27002 control apply, and why?
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS soa (
                item_id TEXT PRIMARY KEY,                    -- control, e.g. "8.13"
                status  TEXT NOT NULL DEFAULT 'ikke_vurdert',
                notes   TEXT NOT NULL DEFAULT ''             -- the justification
            )
            """
        )
        # v5: status per NSM measure (tiltak), e.g. "2.6.4"
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS measures (
                item_id TEXT PRIMARY KEY,
                status  TEXT NOT NULL DEFAULT 'ikke_startet',
                notes   TEXT NOT NULL DEFAULT ''
            )
            """
        )
        # v5: residual risk = likelihood and impact after the measures (NULL = not assessed yet).
        # A database made by v2-v4 lacks these columns, so they are added if missing.
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(risks)")]
        for column in ("residual_likelihood", "residual_impact"):
            if column not in columns:
                conn.execute(f"ALTER TABLE risks ADD COLUMN {column} INTEGER")
        # v8: the incident log. risk_id links to a risk; it is set to NULL when that risk is deleted.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                date         TEXT NOT NULL,             -- YYYY-MM-DD, when it was discovered
                title        TEXT NOT NULL,
                description  TEXT NOT NULL DEFAULT '',
                severity     TEXT NOT NULL,             -- lav / middels / hoy
                status       TEXT NOT NULL DEFAULT 'apen',
                principle_id TEXT NOT NULL DEFAULT '',
                risk_id      INTEGER,                   -- linked risk, or NULL
                gdpr         INTEGER NOT NULL DEFAULT 0, -- 1 = personal data breach
                lessons      TEXT NOT NULL DEFAULT ''   -- corrective action and what was learned
            )
            """
        )
        # v9: progress history, at most one row per day (see record_history)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                date           TEXT PRIMARY KEY,        -- YYYY-MM-DD
                principles     INTEGER NOT NULL,        -- % of NSM's principles (0-100)
                measures       INTEGER NOT NULL,        -- % of NSM's measures
                isms           INTEGER NOT NULL,        -- % of ISO 27001 clauses 4-10
                soa            INTEGER NOT NULL,        -- % of the 93 controls assessed in the SoA
                open_risks     INTEGER NOT NULL,
                open_incidents INTEGER NOT NULL
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
        _upsert_progress(conn, principle_id, status, notes, iso_ref, gdpr)


def _upsert_progress(conn, principle_id, status, notes, iso_ref, gdpr):
    """The SQL for save_progress, on an open connection (import_all uses it too)."""
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
               "actions", "principle_id", "status", "review_date", "gdpr",
               "residual_likelihood", "residual_impact"]


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
    with connect() as conn:
        _insert_risk(conn, data)


def _insert_risk(conn, data):
    columns = ", ".join(RISK_FIELDS)
    placeholders = ", ".join("?" for _ in RISK_FIELDS)
    # Returns the cursor, so import_all can read the new risk's id (lastrowid)
    return conn.execute(f"INSERT INTO risks ({columns}) VALUES ({placeholders})",
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
        # v8: incidents linked to this risk keep their data, but lose the link
        conn.execute("UPDATE incidents SET risk_id = NULL WHERE risk_id = ?", (risk_id,))


# ---------- v8: incident log ----------

INCIDENT_FIELDS = ["date", "title", "description", "severity", "status",
                   "principle_id", "risk_id", "gdpr", "lessons"]


def get_all_incidents():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM incidents").fetchall()
    return [dict(row) for row in rows]


def get_incident(incident_id):
    with connect() as conn:
        row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return dict(row) if row else None


def add_incident(data):
    with connect() as conn:
        _insert_incident(conn, data)


def _insert_incident(conn, data):
    columns = ", ".join(INCIDENT_FIELDS)
    placeholders = ", ".join("?" for _ in INCIDENT_FIELDS)
    conn.execute(f"INSERT INTO incidents ({columns}) VALUES ({placeholders})",
                 [data[field] for field in INCIDENT_FIELDS])


def update_incident(incident_id, data):
    assignments = ", ".join(f"{field} = ?" for field in INCIDENT_FIELDS)
    with connect() as conn:
        conn.execute(f"UPDATE incidents SET {assignments} WHERE id = ?",
                     [data[field] for field in INCIDENT_FIELDS] + [incident_id])


def delete_incident(incident_id):
    with connect() as conn:
        conn.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))


# ---------- v4: ISO 27001 clauses and the statement of applicability ----------

# The SoA statuses: does an ISO 27002 control apply to us?
SOA_STATUSES = {
    "ikke_vurdert": "Ikke vurdert",
    "gjelder": "Gjelder",
    "gjelder_ikke": "Gjelder ikke",
}

# These tables have the same columns (item_id, status, notes), so they share
# the functions below. The table name is checked against this fixed list before
# it is put into the SQL, so user input can never choose a table.
STATUS_TABLES = {"isms": STATUSES, "soa": SOA_STATUSES, "measures": STATUSES}


def get_statuses(table):
    """Return {item_id: row} for every saved row in "isms", "soa" or "measures"."""
    assert table in STATUS_TABLES
    with connect() as conn:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    return {row["item_id"]: row for row in rows}


def save_status(table, item_id, status, notes):
    """Insert or update one row in "isms", "soa" or "measures" (an upsert, like save_progress)."""
    assert table in STATUS_TABLES
    allowed = STATUS_TABLES[table]
    if status not in allowed:
        status = next(iter(allowed))       # the first status is the default
    with connect() as conn:
        _upsert_status(conn, table, item_id, status, notes)


def _upsert_status(conn, table, item_id, status, notes):
    """The SQL for save_status, on an open connection (import_all uses it too)."""
    conn.execute(
        f"""
        INSERT INTO {table} (item_id, status, notes) VALUES (?, ?, ?)
        ON CONFLICT(item_id) DO UPDATE SET
            status = excluded.status,
            notes = excluded.notes
        """,
        (item_id, status, notes.strip()),
    )


# ---------- v7: import ----------

def import_all(data, replace):
    """Save a checked import file (see backup.clean) in one transaction.

    replace=True:  delete everything first, so the file becomes the new data.
    replace=False: merge. Rows in the file overwrite the same id; rows that are
                   only in the database stay. Risks from the file are added,
                   except one that is exactly like a saved risk, so importing
                   the same file twice does not give every risk twice.
                   v8: the same for incidents. v9: a day of history in the file
                   replaces the same day in the database.
    In the file an incident points to a risk by its place in the file's risk list
    ("risk": 0 = the first risk), because ids differ between databases and browsers.
    Returns (risks added, incidents added).

    "with connect()" commits at the end, or rolls everything back on an error,
    so an import is never left half done.
    """
    with connect() as conn:
        if replace:
            for table in ("progress", "risks", "isms", "soa", "measures", "incidents", "history"):
                conn.execute(f"DELETE FROM {table}")
        for principle_id, row in data["progress"].items():
            _upsert_progress(conn, principle_id, row["status"], row["notes"],
                             row["iso_ref"], row["gdpr"])
        for table in STATUS_TABLES:
            for item_id, row in data[table].items():
                _upsert_status(conn, table, item_id, row["status"], row["notes"])

        # Each saved risk as a tuple of its values -> its id, to spot exact copies
        columns = ", ".join(RISK_FIELDS)
        saved = {tuple(row[1:]): row[0] for row in conn.execute(f"SELECT id, {columns} FROM risks")}
        added = 0
        risk_ids = []                           # the database id of each risk in the file, in order
        for risk in data["risks"]:
            values = tuple(int(risk[f]) if f == "gdpr" else risk[f] for f in RISK_FIELDS)
            if values in saved:
                risk_ids.append(saved[values])  # already saved: link incidents to that one
                continue
            risk_ids.append(_insert_risk(conn, risk).lastrowid)
            added += 1

        # v8: incidents, with the link turned from a place in the file into a database id
        columns = ", ".join(INCIDENT_FIELDS)
        saved = {tuple(row) for row in conn.execute(f"SELECT {columns} FROM incidents")}
        added_incidents = 0
        for incident in data["incidents"]:
            row = {**incident, "risk_id": None if incident["risk"] is None else risk_ids[incident["risk"]]}
            values = tuple(int(row[f]) if f == "gdpr" else row[f] for f in INCIDENT_FIELDS)
            if values in saved:
                continue
            _insert_incident(conn, row)
            added_incidents += 1

        # v9: history. A day in the file replaces the same day in the database.
        for row in data["history"]:
            _upsert_history(conn, row)
    return added, added_incidents


# ---------- v9: progress history ----------

HISTORY_FIELDS = ["principles", "measures", "isms", "soa", "open_risks", "open_incidents"]


def get_history():
    """Every saved day, oldest first."""
    with connect() as conn:
        rows = conn.execute("SELECT * FROM history ORDER BY date").fetchall()
    return [dict(row) for row in rows]


def record_history(day, values):
    """Save today's numbers, at most one row per day.

    Today's row is replaced each time. If the numbers are the same as on the last
    earlier day, today's row is left out, so the graph only gets a new point on
    days when something actually changed. static-history.js uses the same rule.
    """
    with connect() as conn:
        _record_history(conn, day, values)


def _record_history(conn, day, values):
    conn.execute("DELETE FROM history WHERE date = ?", (day,))
    last = conn.execute("SELECT * FROM history WHERE date < ? ORDER BY date DESC LIMIT 1", (day,)).fetchone()
    if last and all(last[field] == values[field] for field in HISTORY_FIELDS):
        return
    _upsert_history(conn, {"date": day, **values})


def _upsert_history(conn, row):
    columns = ", ".join(["date"] + HISTORY_FIELDS)
    placeholders = ", ".join("?" for _ in range(len(HISTORY_FIELDS) + 1))
    conn.execute(f"INSERT OR REPLACE INTO history ({columns}) VALUES ({placeholders})",
                 [row["date"]] + [row[field] for field in HISTORY_FIELDS])

