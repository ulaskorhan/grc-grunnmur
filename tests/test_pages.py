"""Every page loads, user text is escaped, and the public build has no local data."""

import pytest

from app import app
from conftest import RISK_FORM

PAGES = ["/", "/kategori/identifisere", "/risikoer", "/risikoer/ny", "/avvik", "/avvik/ny",
         "/iso27002", "/styringssystem", "/tiltak", "/rapport", "/data", "/om"]


@pytest.mark.parametrize("url", PAGES)
def test_page_loads(client, url):
    assert client.get(url).status_code == 200


def test_risk_title_is_escaped(client):
    client.post("/risikoer/ny", data={**RISK_FORM, "title": "<script>alert(1)</script>"})
    html = client.get("/risikoer").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_reminder_shows_on_the_homepage(client):
    client.post("/risikoer/ny", data={**RISK_FORM, "review_date": "2000-01-01"})
    html = client.get("/").get_data(as_text=True)
    assert "Trenger oppfølging" in html and "Forfalt for" in html


@pytest.mark.parametrize("url", PAGES)
def test_public_build_contains_no_local_data(client, monkeypatch, url):
    # Save something locally, then render the page the way build.py does.
    # The overdue review date makes the risk show up in the homepage reminders too.
    client.post("/risikoer/ny", data={**RISK_FORM, "title": "HEMMELIG-RISIKO", "review_date": "2000-01-01"})
    client.post("/prinsipp/1.1", data={"status": "delvis", "notes": "HEMMELIG-NOTAT"})
    client.post("/avvik/ny", data={"date": "2026-11-01", "title": "HEMMELIG-AVVIK",
                                   "severity": "hoy", "status": "apen"})
    monkeypatch.setitem(app.config, "STATIC_SITE", True)
    html = client.get(url).get_data(as_text=True)
    assert "HEMMELIG" not in html
