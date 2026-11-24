"""Security: forms from other websites are refused, only local host names are answered,
and every page carries the content security policy (see SECURITY.md)."""

from app import app
from conftest import RISK_FORM


def test_form_from_another_website_is_refused(client):
    response = client.post("/risikoer/ny", data=RISK_FORM, headers={"Origin": "https://evil.example"})
    assert response.status_code == 403
    assert "Tap av bilder" not in client.get("/risikoer").get_data(as_text=True)   # nothing was saved


def test_cross_site_fetch_metadata_is_refused(client):
    response = client.post("/prinsipp/1.1", data={"status": "delvis"}, headers={"Sec-Fetch-Site": "cross-site"})
    assert response.status_code == 403


def test_form_from_the_app_itself_works(client):
    response = client.post("/risikoer/ny", data=RISK_FORM,
                           headers={"Origin": "http://localhost", "Sec-Fetch-Site": "same-origin"})
    assert response.status_code == 302


def test_unknown_host_name_is_refused(client):
    # A DNS-rebinding page reaches 127.0.0.1 under its own name
    assert client.get("/", base_url="http://evil.example").status_code == 400
    assert client.get("/", base_url="http://127.0.0.1:5050").status_code == 200


def test_every_page_has_the_security_policy(client):
    response = client.get("/")
    html = response.get_data(as_text=True)
    assert "Content-Security-Policy" in html and "script-src 'self'" in html
    assert response.headers["X-Frame-Options"] == "DENY"


def test_no_inline_scripts_or_handlers(client, monkeypatch):
    # The policy blocks inline code, so none may be left in the pages (it would silently break)
    monkeypatch.setitem(app.config, "STATIC_SITE", True)
    for url in ["/", "/risikoer/ny", "/avvik/ny", "/rapport", "/data", "/om", "/iso27002"]:
        html = client.get(url).get_data(as_text=True)
        assert "<script>" not in html, url
        for handler in (" onclick=", " onsubmit=", " onload=", " onchange="):
            assert handler not in html, (url, handler)
