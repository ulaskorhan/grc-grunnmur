"""Export and import (backup.py and db.import_all)."""

import json
import io

import backup
import db
from conftest import RISK_FORM


def export(client):
    return json.loads(client.get("/data/eksport").get_data(as_text=True))


def upload(client, data, mode):
    file = (io.BytesIO(json.dumps(data).encode()), "grunnmur.json")
    return client.post("/data/import", data={"file": file, "mode": mode},
                       content_type="multipart/form-data")


def test_export_then_clean_gives_the_same_data(client):
    client.post("/risikoer/ny", data=RISK_FORM)
    client.post("/prinsipp/2.6", data={"status": "delvis", "notes": "NAS", "iso_ref": "A.5.15"})
    data = export(client)
    cleaned, error = backup.clean(data)
    assert error is None
    assert cleaned["risks"][0]["title"] == "Tap av bilder"
    assert cleaned["progress"]["2.6"]["status"] == "delvis"


def test_merging_the_same_file_twice_adds_no_copies(client):
    client.post("/risikoer/ny", data=RISK_FORM)
    data = export(client)
    upload(client, data, "sammen")
    assert len(db.get_all_risks()) == 1


def test_replace_deletes_what_was_there(client):
    client.post("/risikoer/ny", data=RISK_FORM)
    data = export(client)
    client.post("/risikoer/ny", data={**RISK_FORM, "title": "Ekstra"})
    upload(client, data, "erstatt")
    assert [r["title"] for r in db.get_all_risks()] == ["Tap av bilder"]


def test_a_bad_file_changes_nothing(client):
    client.post("/risikoer/ny", data=RISK_FORM)
    data = export(client)
    data["risks"].append({**data["risks"][0], "likelihood": 9})   # one wrong value
    response = upload(client, data, "erstatt")
    assert response.status_code == 400
    assert "Risiko nr. 2" in response.get_data(as_text=True)
    assert len(db.get_all_risks()) == 1


def test_files_from_other_apps_are_refused():
    assert backup.clean({"app": "noe-annet", "format": 1})[1] == "Filen er ikke en eksport fra Grunnmur."
    assert backup.clean({"app": "grunnmur", "format": 99})[1].startswith("Filen har et format")
    assert "ukjent nummer" in backup.clean({"app": "grunnmur", "format": 1,
                                            "progress": {"9.9": {"status": "delvis"}}})[1]
