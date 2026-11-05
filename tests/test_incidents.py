"""The incident log (v8): form rules, pages, risk links, and export/import."""

import io
import json

import pytest

import backup
import db
import incidents
from conftest import RISK_FORM

INCIDENT_FORM = {"date": "2026-11-01", "title": "Phishing-lenke åpnet", "description": "",
                 "severity": "hoy", "status": "apen", "principle_id": "2.7",
                 "risk_id": "", "lessons": "Totrinn på alle kontoer"}


@pytest.mark.parametrize("change, message", [
    ({"title": " "}, "Avviket må ha en tittel."),
    ({"date": ""}, "Velg datoen avviket ble oppdaget."),
    ({"date": "20261101"}, "Velg datoen avviket ble oppdaget."),
    ({"date": "2026-02-30"}, "Velg datoen avviket ble oppdaget."),
    ({"severity": "katastrofe"}, "Velg en gyldig alvorlighet."),
    ({"status": "glemt"}, "Velg en gyldig status."),
    ({"principle_id": "9.9"}, "Ukjent NSM-prinsipp."),
    ({"risk_id": "7"}, "Ukjent risiko."),
])
def test_invalid_form_is_refused(change, message):
    assert incidents.read_form({**INCIDENT_FORM, **change}, {1, 2})[1] == message


def test_open_incidents_most_severe_then_newest():
    rows = [{"id": 1, "severity": "lav", "status": "apen", "date": "2026-11-03"},
            {"id": 2, "severity": "hoy", "status": "apen", "date": "2026-10-01"},
            {"id": 3, "severity": "hoy", "status": "under_behandling", "date": "2026-11-02"},
            {"id": 4, "severity": "hoy", "status": "lukket", "date": "2026-11-04"}]
    found = incidents.open_incidents(rows)
    assert [item["id"] for item in found] == [3, 2, 1]
    assert found[0]["when"] == "Avvik under behandling · Høy"


def add_risk_and_incident(client):
    client.post("/risikoer/ny", data=RISK_FORM)
    risk_id = db.get_all_risks()[0]["id"]
    client.post("/avvik/ny", data={**INCIDENT_FORM, "risk_id": str(risk_id), "gdpr": "on"})
    return risk_id


def test_incident_is_saved_and_listed_with_its_risk(client):
    add_risk_and_incident(client)
    html = client.get("/avvik").get_data(as_text=True)
    assert "Phishing-lenke åpnet" in html
    assert "Risiko: Tap av bilder" in html
    assert "Personopplysningsbrudd" in html
    assert "01.11.2026" in html


def test_open_incident_shows_on_the_homepage(client):
    add_risk_and_incident(client)
    assert "Åpent avvik · Høy" in client.get("/").get_data(as_text=True)


def test_deleting_a_risk_keeps_the_incident_without_the_link(client):
    risk_id = add_risk_and_incident(client)
    client.post(f"/risikoer/{risk_id}/slett")
    incident = db.get_all_incidents()[0]
    assert incident["risk_id"] is None and incident["title"] == "Phishing-lenke åpnet"


def test_edit_and_delete(client):
    client.post("/avvik/ny", data=INCIDENT_FORM)
    incident_id = db.get_all_incidents()[0]["id"]
    client.post(f"/avvik/{incident_id}", data={**INCIDENT_FORM, "status": "lukket"})
    assert db.get_incident(incident_id)["status"] == "lukket"
    client.post(f"/avvik/{incident_id}/slett")
    assert db.get_all_incidents() == []


def upload(client, data, mode):
    file = (io.BytesIO(json.dumps(data).encode()), "grunnmur.json")
    return client.post("/data/import", data={"file": file, "mode": mode},
                       content_type="multipart/form-data")


def test_export_and_import_keep_the_link_to_the_risk(client):
    add_risk_and_incident(client)
    client.post("/risikoer/ny", data={**RISK_FORM, "title": "En risiko til"})
    data = json.loads(client.get("/data/eksport").get_data(as_text=True))
    assert data["format"] == 2
    assert data["incidents"][0]["risk"] == 0          # the first risk in the file

    upload(client, data, "erstatt")                    # new ids in the database
    incident = db.get_all_incidents()[0]
    assert db.get_risk(incident["risk_id"])["title"] == "Tap av bilder"

    upload(client, data, "sammen")                     # the same file again: no copies
    assert len(db.get_all_incidents()) == 1 and len(db.get_all_risks()) == 2


def test_a_format_1_file_is_still_accepted():
    cleaned, error = backup.clean({"app": "grunnmur", "format": 1, "risks": []})
    assert error is None and cleaned["incidents"] == []


def test_an_incident_pointing_to_a_missing_risk_is_refused():
    item = {"date": "2026-11-01", "title": "x", "severity": "lav", "status": "apen", "risk": 3}
    _cleaned, error = backup.clean({"app": "grunnmur", "format": 2, "risks": [], "incidents": [item]})
    assert error == "Avvik nr. 1: Ukjent risiko."
