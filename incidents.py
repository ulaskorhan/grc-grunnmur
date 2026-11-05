"""Incident log (v8): security incidents and deviations (avvik), and what was learned.

Maps to ISO 27001 clause 10.2 (deviations and corrective action) and the incident
controls in ISO 27002 5.24-5.28, among them 5.27: learn from incidents.
An incident can be linked to an NSM principle and to a risk in the register,
so it shows which risk turned into a real event.

The same rules are sent to the browser as JSON (config_for_browser), so the
GitHub Pages version (static-incidents.js) checks a form exactly like this file.
"""

import re
from datetime import date

import nsm_data

SEVERITIES = {"lav": "Lav", "middels": "Middels", "hoy": "Høy"}
STATUSES = {"apen": "Åpen", "under_behandling": "Under behandling", "lukket": "Lukket"}

# Values a new, empty form starts with. "date" is filled with today when the form opens.
DEFAULTS = {
    "date": "", "title": "", "description": "", "severity": "middels",
    "status": "apen", "principle_id": "", "risk_id": None, "gdpr": False, "lessons": "",
}

# A worked example behind the "Eksempel" button. Written for Grunnmur, not from NSM or ISO.
EXAMPLE = {
    "title": "Phishing-lenke åpnet på laptopen",
    "description": "En e-post som lignet en pakkevarsling ble åpnet, og passordet til e-posten "
                   "ble skrevet inn på en falsk side. Oppdaget samme kveld.",
    "severity": "Høy",
    "principle": "2.7 Kontroller identiteter og tilganger",
    "lessons": "Byttet passord og slo på totrinnsinnlogging. Sjekket at ingen regler for "
               "videresending var lagt til. Lærdom: totrinn på alle kontoer som har det.",
}

# GDPR art. 33, in my own words. Shown on the form and on incidents marked as a personal data breach.
GDPR_NOTE = ("Et brudd på personopplysningssikkerheten skal meldes til Datatilsynet uten ugrunnet "
             "opphold og om mulig innen 72 timer etter at det ble oppdaget, med mindre det er lite "
             "sannsynlig at det gir risiko for personene det gjelder (GDPR art. 33).")


def read_form(form, risk_ids):
    """Read and check the incident form. Returns (data, error).

    risk_ids is the set of risk ids that exist, so a link can only point to a real risk.
    error is a Norwegian message, or None when everything is valid.
    """
    risk_text = form.get("risk_id", "").strip()
    data = {
        "date": form.get("date", "").strip(),
        "title": form.get("title", "").strip()[:200],
        "description": form.get("description", "").strip(),
        "severity": form.get("severity", ""),
        "status": form.get("status", ""),
        "principle_id": form.get("principle_id", ""),
        "risk_id": int(risk_text) if risk_text.isdigit() else None,
        "gdpr": "gdpr" in form,                 # a checkbox is only sent when it is ticked
        "lessons": form.get("lessons", "").strip(),
    }
    if not data["title"]:
        return data, "Avviket må ha en tittel."
    # Exactly YYYY-MM-DD (fromisoformat alone also accepts e.g. "20261101"), and a real day
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["date"]):
            raise ValueError
        date.fromisoformat(data["date"])
    except ValueError:
        return data, "Velg datoen avviket ble oppdaget."
    if data["severity"] not in SEVERITIES:
        return data, "Velg en gyldig alvorlighet."
    if data["status"] not in STATUSES:
        return data, "Velg en gyldig status."
    if data["principle_id"] and data["principle_id"] not in nsm_data.PRINCIPLE_IDS:
        return data, "Ukjent NSM-prinsipp."
    if risk_text and data["risk_id"] not in risk_ids:
        return data, "Ukjent risiko."
    return data, None


def enrich(incident, risk_titles):
    """Add the labels a page needs. risk_titles maps risk id -> title."""
    item = dict(incident)
    item["severity_label"] = SEVERITIES[item["severity"]]
    item["status_label"] = STATUSES[item["status"]]
    item["risk_title"] = risk_titles.get(item["risk_id"], "")
    # dd.mm.yyyy, the way dates are written in Norway
    item["date_label"] = date.fromisoformat(item["date"]).strftime("%d.%m.%Y")
    return item


def sort_key(item):
    """Open incidents first, then the newest first."""
    return (item["status"] == "lukket", -date.fromisoformat(item["date"]).toordinal(), item["title"].lower())


def open_incidents(items):
    """Incidents that are not closed, for the homepage reminders: most severe first, then newest."""
    order = list(SEVERITIES)                    # lav, middels, hoy
    found = [item for item in items if item["status"] != "lukket"]
    found.sort(key=lambda item: item["date"], reverse=True)                     # newest first ...
    found.sort(key=lambda item: order.index(item["severity"]), reverse=True)    # ... within each severity
    for item in found:
        item["when"] = reminder_text(item)
    return found


def reminder_text(item):
    """E.g. "Åpent avvik · Høy" (static/reminders.js writes the same)."""
    state = "Åpent avvik" if item["status"] == "apen" else "Avvik under behandling"
    return f"{state} · {SEVERITIES[item['severity']]}"


def config_for_browser():
    """The rules above as plain data, for static-incidents.js on GitHub Pages."""
    return {"severities": SEVERITIES, "statuses": STATUSES}
