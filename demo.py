"""Example data (eksempeldata): a fictional home lab, for visitors who want to see the tool in use.

The Data page on GitHub Pages has a button "Prøv med eksempeldata". It loads this data into
the visitor's own browser with the same import as a file (static/data.js), so it is checked
by the same rules. A test (tests/test_demo.py) checks that backup.clean() accepts it.

Everything here is made up: a small home lab with a NAS, a few laptops and a router.
The texts are in my own words. Only NSM's numbers and the ISO control numbers are real.

Dates are counted back from the day the page is built, so the example always looks current.
The public site is rebuilt at least every third day (the cyber level check).
"""

from datetime import date, timedelta

import backup

# Principles: status and a short note. Not listed = not started.
PROGRESS = {
    "1.1": ("implementert", "Eksempel: oversikt over hjemmelaben, hvem som bruker den og hva som er viktigst (bilder og dokumenter)."),
    "1.2": ("implementert", "Eksempel: liste over alle enheter og programvare i et regneark, oppdatert hver måned."),
    "1.3": ("delvis", "Eksempel: brukerne er kartlagt, men gjestetilgang er ikke vurdert ennå."),
    "2.1": ("delvis", ""),
    "2.2": ("delvis", "Eksempel: eget nett for IoT-enheter er planlagt."),
    "2.3": ("implementert", "Eksempel: automatiske oppdateringer på alle maskiner og på ruteren."),
    "2.4": ("delvis", ""),
    "2.6": ("implementert", "Eksempel: ingen bruker daglig med administratorrettigheter. MFA på e-post og NAS."),
    "2.7": ("delvis", "Eksempel: diskkryptering på laptopene, ikke på NAS ennå."),
    "2.8": ("implementert", ""),
    "2.9": ("implementert", "Eksempel: 3-2-1-backup av NAS, gjenoppretting testet hver tredje måned."),
    "3.1": ("delvis", ""),
    "4.1": ("delvis", "Eksempel: en enkel plan for hva som gjøres ved løsepengevirus."),
    "4.4": ("delvis", ""),
}
# GDPR flag on the principles that handle personal data in the example
GDPR = {"1.3", "2.6", "2.9"}

# NSM's 15 measures in priority group 1, and a few more
MEASURES = {
    "1.2.3": "implementert", "1.2.4": "implementert", "2.1.2": "delvis", "2.1.9": "delvis",
    "2.2.3": "delvis", "2.3.1": "implementert", "2.3.2": "delvis", "2.3.3": "implementert",
    "2.3.7": "implementert", "2.6.4": "implementert", "2.6.5": "delvis", "2.9.1": "implementert",
    "3.2.3": "delvis", "4.1.1": "delvis", "1.1.1": "implementert", "1.1.2": "delvis",
    "1.2.1": "implementert", "1.3.1": "delvis",
}

# ISO 27001 clauses 4-10
ISMS = {
    "4.1": "implementert", "4.2": "implementert", "4.3": "implementert", "5.1": "delvis",
    "5.2": "delvis", "6.1.2": "implementert", "6.1.3": "delvis", "7.5": "delvis",
    "8.2": "implementert", "9.1": "delvis", "10.2": "delvis",
}

# Statement of applicability: (status, reason)
SOA = {
    "5.15": ("gjelder", "Hvem som har tilgang til NAS og ruteren."),
    "5.17": ("gjelder", "Passordhåndterer for alle i husstanden."),
    "5.23": ("gjelder", "Bilder synkroniseres til en skytjeneste."),
    "5.24": ("gjelder", "Enkel plan for hendelser."),
    "5.30": ("gjelder", "Backup må kunne gjenopprettes innen en dag."),
    "6.3": ("gjelder", "Alle i husstanden kjenner igjen phishing."),
    "7.4": ("gjelder_ikke", "Ingen fysisk overvåking i en privat bolig."),
    "8.1": ("gjelder", "Laptoper og telefoner."),
    "8.5": ("gjelder", "MFA der det er mulig."),
    "8.7": ("gjelder", "Innebygd vern mot skadevare på alle maskiner."),
    "8.8": ("gjelder", "Automatiske oppdateringer."),
    "8.11": ("gjelder_ikke", "Ingen testdata eller utvikling med personopplysninger."),
    "8.13": ("gjelder", "3-2-1-backup av NAS."),
    "8.15": ("gjelder", "Logger fra ruteren og NAS."),
    "8.20": ("gjelder", "Eget gjestenett og IoT-nett."),
    "8.24": ("gjelder", "Diskkryptering og HTTPS."),
}


def _risks(today):
    """Four risks: one overdue for review, one due soon, one accepted and one closed."""
    day = lambda offset: (today + timedelta(days=offset)).isoformat()
    return [
        {"title": "Løsepengevirus krypterer NAS", "likelihood": 3, "impact": 5,
         "residual_likelihood": 2, "residual_impact": 3, "treatment": "redusere",
         "description": "Skadevare på en laptop når NAS-en via delte mapper.",
         "actions": "Frakoblet backup hver uke, skrivebeskyttede øyeblikksbilder, ingen admin-rettigheter i daglig bruk.",
         "principle_id": "2.9", "status": "under_behandling", "review_date": day(-4), "gdpr": True},
        {"title": "Standardpassord på IoT-enheter", "likelihood": 4, "impact": 3,
         "residual_likelihood": 2, "residual_impact": 2, "treatment": "redusere",
         "description": "Kamera og smartpærer kan ha fabrikkpassord og gammel programvare.",
         "actions": "Bytte alle passord, flytte enhetene til et eget nett.",
         "principle_id": "2.3", "status": "apen", "review_date": day(9), "gdpr": False},
        {"title": "Phishing mot familiens e-post", "likelihood": 3, "impact": 3,
         "residual_likelihood": 2, "residual_impact": 3, "treatment": "redusere",
         "description": "En falsk innloggingsside lurer til seg et passord.",
         "actions": "MFA på alle e-postkontoer og en kort gjennomgang av hvordan phishing ser ut.",
         "principle_id": "2.8", "status": "apen", "review_date": day(45), "gdpr": True},
        {"title": "Strømbrudd under oppdatering av NAS", "likelihood": 2, "impact": 2,
         "residual_likelihood": None, "residual_impact": None, "treatment": "akseptere",
         "description": "Et strømbrudd midt i en oppdatering kan ødelegge systemdisken.",
         "actions": "Akseptert: backupen dekker dette. UPS vurderes neste år.",
         "principle_id": "2.9", "status": "lukket", "review_date": day(120), "gdpr": False},
    ]


def _incidents(today):
    """Three incidents. "risk" is the place in the risk list above (0 = the first risk)."""
    day = lambda offset: (today + timedelta(days=offset)).isoformat()
    return [
        {"date": day(-3), "title": "Ukjent enhet på gjestenettet", "severity": "middels",
         "status": "under_behandling", "principle_id": "3.2", "risk": 1, "gdpr": False,
         "description": "Ruteren varslet om en ny enhet som ingen kjente igjen.",
         "lessons": ""},
        {"date": day(-11), "title": "Phishing-e-post åpnet", "severity": "hoy",
         "status": "lukket", "principle_id": "4.3", "risk": 2, "gdpr": True,
         "description": "En lenke i en falsk pakkevarsling ble åpnet, men ingen passord ble skrevet inn.",
         "lessons": "Passord byttet for sikkerhets skyld. MFA slått på for alle kontoer."},
        {"date": day(-19), "title": "Backupjobb feilet i tre dager", "severity": "lav",
         "status": "lukket", "principle_id": "2.9", "risk": None, "gdpr": False,
         "description": "Disken til den eksterne backupen var full.",
         "lessons": "Varsel på e-post når en backupjobb feiler."},
    ]


def _snapshot(data, ids):
    """The numbers the history stores for this data (the same rules as app.progress_snapshot).

    ids are the lists each percentage is counted over (app.history_ids()).
    """
    score = {"ikke_startet": 0, "delvis": 0.5, "implementert": 1}
    percent = lambda keys, rows: round(100 * sum(score[rows[k]["status"]] for k in keys if k in rows) / len(keys))
    assessed = sum(1 for k in ids["soa"] if k in data["soa"] and data["soa"][k]["status"] != "ikke_vurdert")
    return {
        "principles": percent(ids["principles"], data["progress"]),
        "measures": percent(ids["measures"], data["measures"]),
        "isms": percent(ids["isms"], data["isms"]),
        "soa": round(100 * assessed / len(ids["soa"])),
        "open_risks": sum(1 for r in data["risks"] if r["status"] != "lukket"),
        "open_incidents": sum(1 for i in data["incidents"] if i["status"] != "lukket"),
    }


def _history(today, final):
    """Six days over three weeks, growing towards today's real numbers.

    The last day is exactly what the data adds up to, so the graph ends where the
    rest of the app is. The earlier days are made up, like everything else here.
    """
    share = [0.25, 0.4, 0.55, 0.7, 0.85, 1]
    rows = []
    for number, part in enumerate(share):
        row = {"date": (today - timedelta(days=4 * (len(share) - 1 - number))).isoformat()}
        for key in ("principles", "measures", "isms", "soa"):
            row[key] = round(final[key] * part)
        row["open_risks"] = final["open_risks"] + (1 if number < 3 else 0)
        row["open_incidents"] = final["open_incidents"] + (1 if 1 <= number < 4 else 0)
        rows.append(row)
    return rows


def example_file(ids, today=None):
    """The whole example as an export file (format 3), ready for the import.

    ids comes from app.history_ids(), so the last history day matches the rest of the data.
    """
    today = today or date.today()
    data = {
        "app": backup.APP, "format": backup.FORMAT, "exported": today.isoformat(),
        "progress": {pid: {"status": status, "notes": notes, "iso_ref": "", "gdpr": pid in GDPR}
                     for pid, (status, notes) in PROGRESS.items()},
        "measures": {mid: {"status": status, "notes": ""} for mid, status in MEASURES.items()},
        "isms": {iid: {"status": status, "notes": ""} for iid, status in ISMS.items()},
        "soa": {cid: {"status": status, "notes": notes} for cid, (status, notes) in SOA.items()},
        "risks": _risks(today),
        "incidents": _incidents(today),
    }
    data["history"] = _history(today, _snapshot(data, ids))
    return data
