"""Progress history (v9): the one-row-per-day rule, recording after saves, export/import."""

import io
import json

import backup
import db
from app import app
from conftest import RISK_FORM

ZERO = {field: 0 for field in db.HISTORY_FIELDS}


def test_a_day_like_the_last_one_gets_no_row(client):
    db.record_history("2026-11-01", {**ZERO, "principles": 10})
    db.record_history("2026-11-02", {**ZERO, "principles": 10})     # nothing changed
    db.record_history("2026-11-03", {**ZERO, "principles": 20})
    assert [row["date"] for row in db.get_history()] == ["2026-11-01", "2026-11-03"]


def test_the_same_day_is_replaced(client):
    db.record_history("2026-11-01", {**ZERO, "measures": 5})
    db.record_history("2026-11-01", {**ZERO, "measures": 7})
    assert [(row["date"], row["measures"]) for row in db.get_history()] == [("2026-11-01", 7)]


def test_saving_a_form_records_today(client):
    client.post("/prinsipp/1.1", data={"status": "implementert"})
    client.post("/risikoer/ny", data=RISK_FORM)
    rows = db.get_history()
    assert len(rows) == 1                                  # one row for today
    assert rows[0]["principles"] == round(100 / 21) and rows[0]["open_risks"] == 1


def test_a_refused_form_records_nothing(client):
    client.post("/risikoer/ny", data={**RISK_FORM, "title": ""})   # 400, nothing saved
    assert db.get_history() == []


def test_report_contains_the_history(client):
    client.post("/prinsipp/1.1", data={"status": "delvis"})
    html = client.get("/rapport").get_data(as_text=True)
    assert "Utvikling over tid" in html and '"principles": 2' in html


def test_export_and_import_the_history(client):
    db.record_history("2026-10-01", {**ZERO, "soa": 30})
    data = json.loads(client.get("/data/eksport").get_data(as_text=True))
    assert data["history"][0]["soa"] == 30
    with db.connect() as conn:
        conn.execute("DELETE FROM history")
    file = (io.BytesIO(json.dumps(data).encode()), "g.json")
    client.post("/data/import", data={"file": file, "mode": "sammen"}, content_type="multipart/form-data")
    assert db.get_history()[0] == {"date": "2026-10-01", **ZERO, "soa": 30}


def test_bad_history_is_refused():
    day = {"date": "2026-11-01", **ZERO}
    base = {"app": "grunnmur", "format": 3}
    assert backup.clean({**base, "history": [day, day]})[1] == "Historikk nr. 2: samme dato to ganger."
    assert backup.clean({**base, "history": [{**day, "isms": 101}]})[1].startswith("Historikk nr. 1: «isms»")
    assert backup.clean({**base, "history": [{**day, "date": "1.11.2026"}]})[1] == "Historikk nr. 1: ugyldig dato."


def test_the_public_build_records_nothing(client, monkeypatch):
    monkeypatch.setitem(app.config, "STATIC_SITE", True)
    client.post("/prinsipp/1.1", data={"status": "delvis"})
    assert db.get_history() == []
