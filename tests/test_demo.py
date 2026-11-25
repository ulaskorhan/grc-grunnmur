"""The example data (demo.py) is a valid export file, and adds up to its own last history day."""

from datetime import date

import backup
import db
import demo
from app import app, history_ids, progress_snapshot


def test_example_passes_the_import_checks():
    data, error = backup.clean(demo.example_file(history_ids(), date(2026, 11, 25)))
    assert error is None
    assert len(data["risks"]) == 4 and len(data["incidents"]) == 3 and len(data["history"]) == 6


def test_last_history_day_matches_the_data(client):
    # Import the example like a file, then let the app count it: the graph must end there
    with app.test_request_context():
        data, _error = backup.clean(demo.example_file(history_ids()))
        db.import_all(data, replace=True)
        assert progress_snapshot() == {k: v for k, v in data["history"][-1].items() if k != "date"}


def test_example_is_only_on_the_public_data_page(client, monkeypatch):
    assert 'id="example-data"' not in client.get("/data").get_data(as_text=True)
    monkeypatch.setitem(app.config, "STATIC_SITE", True)
    assert 'id="example-data"' in client.get("/data").get_data(as_text=True)
