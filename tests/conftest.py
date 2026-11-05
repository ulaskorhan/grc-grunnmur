"""Shared setup for the tests.

Every test that touches the database gets its own empty SQLite file in a
temporary folder, so the tests never read or change my real grunnmur.db.
"""

import sys
from pathlib import Path

import pytest

# Let the tests import app.py, db.py, ... from the folder above
sys.path.insert(0, str(Path(__file__).parent.parent))

import db  # noqa: E402
from app import app  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A Flask test client with a fresh, empty database (the local version)."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    monkeypatch.setitem(app.config, "STATIC_SITE", False)
    return app.test_client()


# A valid risk as the form sends it. Tests copy it and change one field.
RISK_FORM = {"title": "Tap av bilder", "likelihood": "3", "impact": "4",
             "treatment": "redusere", "status": "apen", "review_date": "",
             "description": "", "actions": "", "principle_id": ""}
