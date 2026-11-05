"""Export and import (v7): all saved data as one JSON file.

The same file format is used by the Flask version and the GitHub Pages version,
so data can be moved between them, or kept as a backup:

    {
      "app": "grunnmur", "format": 3, "exported": "2026-11-03",
      "progress": { "2.6":   { "status": "delvis", "notes": "...", "iso_ref": "A.5.15", "gdpr": true } },
      "measures": { "2.6.4": { "status": "implementert", "notes": "..." } },
      "isms":     { "6.1.2": { "status": "delvis", "notes": "..." } },
      "soa":      { "8.13":  { "status": "gjelder", "notes": "Backup av NAS" } },
      "risks":    [ { "title": "...", "likelihood": 3, "impact": 4, ... } ],
      "incidents": [ { "date": "2026-11-01", "title": "...", "risk": 0, ... } ],
      "history":  [ { "date": "2026-11-01", "principles": 40, "measures": 12, ... } ]
    }

Format 2 (v8) added "incidents", format 3 (v9) "history". Older files are still
accepted; a part they do not have counts as empty.

Risks have no id in the file: the ids differ between the database (1, 2, 3)
and the browser ("lq3k9x2a"), so the importing side gives each risk a new one.
For the same reason an incident points to a risk by its place in "risks"
("risk": 0 = the first risk), or "risk": null for no link.

A file is checked completely before anything is saved. One wrong value and
nothing is imported, so a broken file can never leave half the data behind.
The browser version (static/data.js) does the same checks with the rules from
rules_for_browser(), so both versions accept the same files.
"""

import re
from datetime import date

import db
import incidents
import iso27001
import iso27002
import nsm_data
import nsm_measures
import risks

APP = "grunnmur"
FORMAT = 3                      # raise this if the file format ever changes
READS = (1, 2, 3)               # formats this version can import
MAX_BYTES = 1_000_000           # 1 MB: far more than a full Grunnmur file needs

# The four parts with one row per id: which ids exist, and which statuses are allowed.
SECTIONS = {
    "progress": (nsm_data.PRINCIPLE_IDS, db.STATUSES),
    "measures": (set(nsm_measures.TITLES), db.STATUSES),
    "isms": (iso27001.ITEM_IDS, db.STATUSES),
    "soa": (set(iso27002.CONTROLS), db.SOA_STATUSES),
}
# Norwegian names for the parts, used in messages and on the Data page
LABELS = {"progress": "Grunnprinsipper", "measures": "Tiltak", "isms": "Styringssystem",
          "soa": "SoA", "risks": "Risikoer", "incidents": "Avvik", "history": "Dager i historikken"}

# The risk fields in the file, in this order
RISK_TEXT = ["title", "description", "treatment", "actions", "principle_id", "status", "review_date"]
RISK_NUMBERS = ["likelihood", "impact", "residual_likelihood", "residual_impact"]
# v8: the incident text fields in the file ("risk" and "gdpr" come after them)
INCIDENT_TEXT = ["date", "title", "description", "severity", "status", "principle_id", "lessons"]


# ---------- Export ----------

def export_data():
    """Everything in the local database, in the file format above."""
    progress = {pid: {"status": row["status"], "notes": row["notes"],
                      "iso_ref": row["iso_ref"], "gdpr": bool(row["gdpr"])}
                for pid, row in db.get_all_progress().items()}
    data = {"app": APP, "format": FORMAT, "exported": date.today().isoformat(),
            "progress": progress}
    for table in ("measures", "isms", "soa"):
        data[table] = {item_id: {"status": row["status"], "notes": row["notes"]}
                       for item_id, row in db.get_statuses(table).items()}
    saved_risks = db.get_all_risks()
    data["risks"] = [_risk_for_file(r) for r in saved_risks]
    # v8: incidents, with the linked risk as its place in the list above
    place = {risk["id"]: number for number, risk in enumerate(saved_risks)}
    data["incidents"] = [_incident_for_file(i, place) for i in db.get_all_incidents()]
    data["history"] = db.get_history()          # v9: already plain rows, oldest first
    return data


def _incident_for_file(incident, place):
    """An incident without its id, with "risk" as a place in the risk list (or None)."""
    item = {field: incident[field] for field in INCIDENT_TEXT}
    item["risk"] = place.get(incident["risk_id"])
    item["gdpr"] = bool(incident["gdpr"])
    return item


def _risk_for_file(risk):
    """A risk from the database without its id, and with gdpr as true/false."""
    item = {field: risk[field] for field in db.RISK_FIELDS}
    item["gdpr"] = bool(item["gdpr"])
    return item


# ---------- Checking an imported file ----------

def clean(data):
    """Check a parsed JSON file. Returns (clean_data, error).

    error is a Norwegian message when something is wrong, otherwise None.
    clean_data holds only known fields, so extra keys in the file are dropped.
    """
    if not isinstance(data, dict) or data.get("app") != APP:
        return None, "Filen er ikke en eksport fra Grunnmur."
    if data.get("format") not in READS:
        return None, "Filen har et format denne versjonen av Grunnmur ikke kjenner."

    result = {}
    for name, (ids, statuses) in SECTIONS.items():
        rows = data.get(name, {})               # a missing part counts as empty
        if not isinstance(rows, dict):
            return None, f"{LABELS[name]}: feil oppbygning i filen."
        result[name] = {}
        for item_id, row in rows.items():
            if item_id not in ids:
                return None, f"{LABELS[name]}: ukjent nummer «{item_id}»."
            if not isinstance(row, dict) or row.get("status") not in statuses:
                return None, f"{LABELS[name]} {item_id}: ugyldig status."
            notes = row.get("notes", "")
            if not isinstance(notes, str):
                return None, f"{LABELS[name]} {item_id}: notatet må være tekst."
            clean_row = {"status": row["status"], "notes": notes.strip()}
            if name == "progress":              # principles also have an ISO reference and a GDPR flag
                iso_ref = row.get("iso_ref", "")
                if not isinstance(iso_ref, str):
                    return None, f"{LABELS[name]} {item_id}: ISO-referansen må være tekst."
                clean_row["iso_ref"] = iso_ref.strip()
                clean_row["gdpr"] = row.get("gdpr") is True
            result[name][item_id] = clean_row

    items = data.get("risks", [])
    if not isinstance(items, list):
        return None, "Risikoer: feil oppbygning i filen."
    result["risks"] = []
    for number, item in enumerate(items, start=1):
        risk, error = _clean_risk(item)
        if error:
            return None, f"Risiko nr. {number}: {error}"
        result["risks"].append(risk)

    # v8: incidents. A format 1 file has none, so a missing list counts as empty.
    items = data.get("incidents", [])
    if not isinstance(items, list):
        return None, "Avvik: feil oppbygning i filen."
    result["incidents"] = []
    for number, item in enumerate(items, start=1):
        incident, error = _clean_incident(item, len(result["risks"]))
        if error:
            return None, f"Avvik nr. {number}: {error}"
        result["incidents"].append(incident)

    # v9: progress history, one row per day
    items = data.get("history", [])
    if not isinstance(items, list):
        return None, "Historikk: feil oppbygning i filen."
    result["history"] = []
    for number, item in enumerate(items, start=1):
        error = _history_error(item, {row["date"] for row in result["history"]})
        if error:
            return None, f"Historikk nr. {number}: {error}"
        result["history"].append({"date": item["date"], **{f: item[f] for f in db.HISTORY_FIELDS}})
    return result, None


def _clean_risk(item):
    """Check one risk with the same rules as the risk form (risks.read_form)."""
    if not isinstance(item, dict):
        return None, "feil oppbygning i filen."
    # read_form() expects form text, so the values are turned into text first.
    # Wrong types are refused here, so e.g. a list can never become the text "[...]".
    form = {}
    for field in RISK_TEXT:
        value = item.get(field, "")
        if not isinstance(value, str):
            return None, f"«{field}» må være tekst."
        form[field] = value
    for field in RISK_NUMBERS:
        value = item.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
            return None, f"«{field}» må være et tall fra 1 til 5."
        form[field] = "" if value is None else str(value)
    if item.get("gdpr") is True:
        form["gdpr"] = "on"                     # like a ticked checkbox
    return risks.read_form(form)


def _clean_incident(item, risk_count):
    """Check one incident with the same rules as the incident form (incidents.read_form)."""
    if not isinstance(item, dict):
        return None, "feil oppbygning i filen."
    form = {}
    for field in INCIDENT_TEXT:
        value = item.get(field, "")
        if not isinstance(value, str):
            return None, f"«{field}» må være tekst."
        form[field] = value
    risk = item.get("risk")
    if risk is not None and (isinstance(risk, bool) or not isinstance(risk, int)):
        return None, "«risk» må være et tall eller null."
    form["risk_id"] = "" if risk is None else str(risk)
    if item.get("gdpr") is True:
        form["gdpr"] = "on"
    # The valid places are 0 .. number of risks in the file - 1
    incident, error = incidents.read_form(form, set(range(risk_count)))
    if error:
        return None, error
    incident["risk"] = incident.pop("risk_id")
    return incident, None


def _history_error(item, seen):
    """Check one day in the history. Returns a message, or None when it is valid."""
    if not isinstance(item, dict) or not isinstance(item.get("date"), str):
        return "feil oppbygning i filen."
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", item["date"]):
            raise ValueError
        date.fromisoformat(item["date"])
    except ValueError:
        return "ugyldig dato."
    if item["date"] in seen:
        return "samme dato to ganger."
    for field in db.HISTORY_FIELDS:
        value = item.get(field)
        highest = 100 if field in ("principles", "measures", "isms", "soa") else 100_000
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= highest:
            return f"«{field}» må være et tall fra 0 til {highest}."
    return None


def counts(data):
    """How many rows each part has, e.g. {"progress": 4, ..., "risks": 2}."""
    return {name: len(data[name]) for name in LABELS}


def rules_for_browser():
    """The rules above as plain data, for static/data.js on GitHub Pages."""
    return {
        "app": APP,
        "format": FORMAT,
        "max_bytes": MAX_BYTES,
        "labels": LABELS,
        "sections": {name: {"ids": sorted(ids), "statuses": list(statuses)}
                     for name, (ids, statuses) in SECTIONS.items()},
        "reads": list(READS),
        "risk": {"treatments": list(risks.TREATMENTS), "statuses": list(risks.STATUSES),
                 "principles": sorted(nsm_data.PRINCIPLE_IDS)},
        "incident": {"severities": list(incidents.SEVERITIES), "statuses": list(incidents.STATUSES)},
        "history_fields": db.HISTORY_FIELDS,
    }
