"""Risk register logic (v2): scales, risk levels, labels and form validation.

A risk is scored the classic way:  score = likelihood × impact  (1-25 on a 5 × 5 matrix).
This maps to ISO 27001 clause 6.1.2 (risk assessment) and 6.1.3 (risk treatment).

The same rules are sent to the browser as JSON (see config_for_browser), so the
GitHub Pages version calculates levels exactly like this file does.
"""

from datetime import date

import nsm_data

# The 1-5 scales. The number is stored; the text explains what it means.
LIKELIHOOD = {1: "Svært usannsynlig", 2: "Lite sannsynlig", 3: "Mulig",
              4: "Sannsynlig", 5: "Svært sannsynlig"}
IMPACT = {1: "Ubetydelig", 2: "Liten", 3: "Moderat", 4: "Alvorlig", 5: "Kritisk"}

# Risk treatment options from ISO 27001 6.1.3. Key is stored, value is shown.
TREATMENTS = {"redusere": "Redusere", "akseptere": "Akseptere",
              "unnga": "Unngå", "overfore": "Overføre"}

STATUSES = {"apen": "Åpen", "under_behandling": "Under behandling", "lukket": "Lukket"}

# Risk levels, highest first: (key, label, lowest score in this level).
# On a 5 × 5 matrix the scores 17-19 cannot happen, so "Høy" is 10-16.
LEVELS = [
    ("kritisk", "Kritisk", 20),
    ("hoy", "Høy", 10),
    ("middels", "Middels", 5),
    ("lav", "Lav", 1),
]

# Values a new, empty form starts with.
DEFAULTS = {
    "title": "", "description": "", "likelihood": 3, "impact": 3,
    "treatment": "redusere", "actions": "", "principle_id": "",
    "status": "apen", "review_date": "", "gdpr": False,
}

# A worked example shown behind the "Eksempel" button on the form.
# Written for Grunnmur, not taken from NSM or ISO.
EXAMPLE = {
    "title": "Løsepengevirus krypterer filene på NAS-en",
    "description": "Skadevare via phishing på laptopen kan nå NAS-en over nettverksdeling "
                   "og kryptere bilder og dokumenter.",
    "score": "Sannsynlighet 3 (Mulig) × Konsekvens 4 (Alvorlig) = 12, Høy",
    "treatment": "Redusere",
    "actions": "Ukentlig kopi til en disk som kobles fra etterpå, og versjonering "
               "(snapshots) på NAS-en. Test gjenoppretting hvert kvartal.",
    "principle": "2.9 Etabler evne til gjenoppretting av data",
}


def risk_level(score):
    """Return (key, label) for a score, e.g. 12 -> ("hoy", "Høy")."""
    for key, label, lowest in LEVELS:
        if score >= lowest:
            return key, label
    return LEVELS[-1][0], LEVELS[-1][1]


def _scale_value(text):
    """Turn form text like "4" into the number 4, or None if it is not 1-5."""
    try:
        number = int(text)
    except (TypeError, ValueError):
        return None
    return number if 1 <= number <= 5 else None


def read_form(form):
    """Check the submitted form. Returns (data, error).

    error is None when everything is valid, otherwise a Norwegian message
    that is shown above the form. The browser also checks some of this, but
    the server must never trust what the browser sends.
    """
    data = {
        "title": form.get("title", "").strip()[:200],
        "description": form.get("description", "").strip(),
        "likelihood": _scale_value(form.get("likelihood")),
        "impact": _scale_value(form.get("impact")),
        "treatment": form.get("treatment", ""),
        "actions": form.get("actions", "").strip(),
        "principle_id": form.get("principle_id", ""),
        "status": form.get("status", ""),
        "review_date": form.get("review_date", "").strip(),
        "gdpr": "gdpr" in form,     # a checkbox is only sent when it is ticked
    }

    if not data["title"]:
        return data, "Risikoen må ha en tittel."
    if data["likelihood"] is None or data["impact"] is None:
        return data, "Velg sannsynlighet og konsekvens fra 1 til 5."
    if data["treatment"] not in TREATMENTS:
        return data, "Velg en gyldig behandling."
    if data["status"] not in STATUSES:
        return data, "Velg en gyldig status."
    if data["principle_id"] and data["principle_id"] not in nsm_data.PRINCIPLE_IDS:
        return data, "Ukjent NSM-prinsipp."
    if data["review_date"]:
        try:
            date.fromisoformat(data["review_date"])   # expects YYYY-MM-DD
        except ValueError:
            return data, "Datoen for neste gjennomgang er ugyldig."
    return data, None


def enrich(risk, today=None):
    """Add the calculated fields a page needs: score, level, labels, overdue."""
    today = today or date.today()
    item = dict(risk)
    item["score"] = item["likelihood"] * item["impact"]
    item["level"], item["level_label"] = risk_level(item["score"])
    item["treatment_label"] = TREATMENTS[item["treatment"]]
    item["status_label"] = STATUSES[item["status"]]
    # Overdue = the review date has passed and the risk is not closed yet.
    item["overdue"] = bool(
        item["review_date"]
        and item["status"] != "lukket"
        and date.fromisoformat(item["review_date"]) < today
    )
    return item


def sort_key(item):
    """Closed risks last, then highest score first, then alphabetical."""
    return (item["status"] == "lukket", -item["score"], item["title"].lower())


def config_for_browser():
    """The rules above as plain data, for static-risks.js on GitHub Pages."""
    return {
        "levels": LEVELS,
        "treatments": TREATMENTS,
        "statuses": STATUSES,
    }
