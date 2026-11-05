"""Grunnmur: a small personal GRC app built on NSM Grunnprinsipper for IKT-sikkerhet.

Run with:  .venv/bin/python app.py   and open http://127.0.0.1:5050

Pages:
  /                     homepage: short intro, the 4 categories with progress, and a list of every part
  /kategori/<id>        one category: its principles, collapsed until clicked
  /prinsipp/<nr> (POST) saves the form for one principle
  /risikoer             v2: the risk register, highest risk first
  /risikoer/ny          v2: form for a new risk
  /risikoer/<id>        v2: edit one risk (POST saves it)
  /risikoer/<id>/slett  v2: delete one risk (POST)
  /iso27002             v3: the 93 ISO/IEC 27002 controls and NSM's links to them
                        v4: plus the statement of applicability (SoA) per control
  /iso27002/soa/<nr>    v4: saves the SoA answer for one control (POST)
  /styringssystem       v4: ISO 27001 clauses 4-10, grouped Plan-Do-Check-Act
  /styringssystem/<nr>  v4: saves one requirement (POST)
  /tiltak               v5: NSM's 118 measures, in NSM's priority groups
  /tiltak/<nr>          v5: saves the status of one measure (POST)
  /rapport              v6: a print-friendly report of everything above (save as PDF from the browser)
  /data                 v7: export and import of all data as one JSON file
  /data/eksport         v7: downloads the JSON file
  /data/import  (POST)  v7: reads an uploaded JSON file, then replaces or merges the data
  /om                   about page: background, and what Grunnmur adds to NSM's advice
"""

import json
from datetime import date

from flask import Flask, abort, redirect, render_template, request, url_for

import backup
import cyber_level
import db
import examples
import incidents
import iso27001
import iso27002
import nsm_data
import nsm_measures
import risks

app = Flask(__name__)
# Tell browsers to re-check style.css on every load, so design changes show up
# immediately instead of an old cached version being used.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
# STATIC_SITE is switched on by build.py when it makes the GitHub Pages version.
# In that mode no data is read from the database, and the browser saves progress instead.
app.config["STATIC_SITE"] = False
# v7: refuse uploads larger than this, before Flask reads them (see too_large below)
app.config["MAX_CONTENT_LENGTH"] = backup.MAX_BYTES

# The public address. Link previews (og:image) need a full URL, not a relative path.
SITE_URL = "https://ulaskorhan.github.io/grc-grunnmur"

# How much each status counts towards the progress score (0-100 %).
SCORE = {"ikke_startet": 0, "delvis": 0.5, "implementert": 1}

# The versions the app was built in, shown on the About page.
ROADMAP = [
    (1, "Grunnprinsipper", "Status, notater, ISO-referanse og personvern per prinsipp"),
    (2, "Risikoregister", "Sannsynlighet × konsekvens, behandling og kobling til NSM og ISO 27001 6.1"),
    (3, "ISO/IEC 27002", "De 93 kontrollene og NSMs egen kobling til grunnprinsippene"),
    (4, "ISO 27001 styringssystem", "Kapittel 4–10 i PDCA-sirkelen og anvendelseserklæring (SoA)"),
    (5, "Tiltak og varmekart", "NSMs tiltak under hvert prinsipp og et risikovarmekart"),
    (6, "Rapport og portefølje", "Utskriftsvennlig rapport og README på engelsk og norsk"),
    (7, "Eksport og import", "Alle data som én JSON-fil, også mellom lokal og offentlig versjon"),
    (8, "Avvikslogg", "Hendelser og avvik med alvorlighet, kobling til risiko og læring (ISO 27001 10.2)"),
]
CURRENT_VERSION = 8

# The side column on the homepage: every part of the app, as (page function, name, text).
SITE_MAP = [
    ("home", "NSMs grunnprinsipper", "21 prinsipper i 4 kategorier, med status og notater"),
    ("measures_page", "Tiltak", "NSMs 118 tiltak, sortert etter NSMs prioritering"),
    ("risk_list", "Risikoregister", "Risikoer før og etter tiltak, med varmekart"),
    ("incident_list", "Avvikslogg", "Hendelser og avvik, og hva du lærte av dem"),
    ("isms_page", "ISO 27001", "Styringssystemet: kapittel 4–10 i PDCA-sirkelen"),
    ("iso_page", "ISO 27002", "De 93 kontrollene og anvendelseserklæringen (SoA)"),
    ("report", "Rapport", "Alt samlet på én side, klar til utskrift eller PDF"),
    ("data_page", "Data", "Eksport og import av alt som én JSON-fil"),
    ("about", "Om", "Bakgrunn, kilder og hva appen ikke er"),
]


@app.context_processor
def add_template_globals():
    """Variables available in every template: static mode, the app version and
    NSM's national cyber risk level (the banner at the top of every page)."""
    return {
        "static_site": app.config["STATIC_SITE"],
        "current_version": CURRENT_VERSION,
        "cyber": cyber_level.for_template(),
        "site_url": SITE_URL,
    }


def load_progress():
    """Read saved progress, except in static mode.

    The public GitHub Pages build must never contain my own local data,
    so it always starts empty. Visitors' progress is saved in their own browser.
    """
    if app.config["STATIC_SITE"]:
        return {}
    return db.get_all_progress()


def load_statuses(table):
    """Like load_progress(), for the tables "isms", "soa" and "measures": empty in static mode."""
    if app.config["STATIC_SITE"]:
        return {}
    return db.get_statuses(table)


def percent_done(item_ids, rows):
    """Progress (0-100) over a list of ids, with the same scoring as the principles."""
    points = sum(SCORE[rows[i]["status"]] for i in item_ids if i in rows)
    return round(100 * points / len(item_ids))


def category_progress(category, progress):
    """Return a category's progress as a whole percentage (0-100).

    A principle with no saved row counts as "ikke_startet".
    """
    points = 0
    for number, _title, _link in category["principles"]:
        row = progress.get(number)
        status = row["status"] if row else "ikke_startet"
        points += SCORE[status]
    return round(100 * points / len(category["principles"]))


def status_counts(category, progress):
    """Count how many principles in a category have each status.

    Returns e.g. {"ikke_startet": 8, "delvis": 1, "implementert": 1}.
    """
    counts = {key: 0 for key in db.STATUSES}
    for number, _title, _link in category["principles"]:
        row = progress.get(number)
        counts[row["status"] if row else "ikke_startet"] += 1
    return counts


@app.route("/")
def home():
    progress = load_progress()
    cards = []
    for category in nsm_data.CATEGORIES:
        cards.append({
            "category": category,
            "percent": category_progress(category, progress),
            "counts": status_counts(category, progress),
        })
    # Number of principles marked "Implementert", shown next to the big ring.
    implemented = sum(card["counts"]["implementert"] for card in cards)
    # Overall progress is the average over all 21 principles, not over the 4 cards,
    # so the large category (10 principles) weighs more than the small ones.
    total = sum(len(c["principles"]) for c in nsm_data.CATEGORIES)
    points = sum(SCORE[row["status"]] for row in progress.values())
    overall = round(100 * points / total)
    # Risks to review soon, and open incidents (v8).
    # Empty in static mode: static/reminders.js fills them from the browser.
    rows = [] if app.config["STATIC_SITE"] else db.get_all_risks()
    return render_template(
        "home.html",
        reminders=risks.reminders(rows),
        open_incidents=incidents.open_incidents(incident_overview()["items"]),
        reminder_days=risks.REMINDER_DAYS,
        cards=cards,
        overall=overall,
        implemented=implemented,
        total=total,
        site_map=SITE_MAP,
        source_url=nsm_data.SOURCE_URL,
        nsm_version=nsm_data.VERSION,
    )


def category_of():
    """Principle number -> category id, e.g. {"2.6": "beskytte"}, to link to its category page."""
    return {number: c["id"] for c in nsm_data.CATEGORIES
            for number, _title, _link in c["principles"]}


@app.route("/iso27002")
def iso_page():
    themes = iso27002.themes_with_controls()
    soa = load_statuses("soa")
    # How many controls have each SoA answer; controls with no saved row are "ikke_vurdert".
    soa_counts = {key: 0 for key in db.SOA_STATUSES}
    for control_id in iso27002.CONTROLS:
        soa_counts[soa[control_id]["status"] if control_id in soa else "ikke_vurdert"] += 1
    return render_template(
        "iso27002.html",
        themes=themes,
        total=len(iso27002.CONTROLS),
        covered=sum(theme["covered"] for theme in themes),
        category_of=category_of(),
        soa=soa,
        soa_counts=soa_counts,
        soa_statuses=db.SOA_STATUSES,
        open_id=request.args.get("apen", ""),
    )


@app.route("/iso27002/soa/<control_id>", methods=["POST"])
def save_soa(control_id):
    if control_id not in iso27002.CONTROLS:
        abort(404)
    db.save_status("soa", control_id,
                   status=request.form.get("status", "ikke_vurdert"),
                   notes=request.form.get("notes", ""))
    return redirect(url_for("iso_page", apen=control_id) + "#k" + control_id)


# ---------- v4: ISO 27001 management system (clauses 4-10) ----------

@app.route("/styringssystem")
def isms_page():
    rows = load_statuses("isms")
    all_ids = [number for clause in iso27001.CLAUSES for number, _title in clause["items"]]
    clauses = {clause["number"]: clause for clause in iso27001.CLAUSES}

    # One card per PDCA phase, with its progress
    phases = []
    for phase_id, name, clause_numbers in iso27001.PHASES:
        ids = [number for n in clause_numbers for number, _title in clauses[n]["items"]]
        phases.append({"id": phase_id, "name": name, "clauses": clause_numbers,
                       "ids": ids, "percent": percent_done(ids, rows)})

    counts = {key: 0 for key in db.STATUSES}
    for number in all_ids:
        counts[rows[number]["status"] if number in rows else "ikke_startet"] += 1

    return render_template(
        "isms.html",
        clauses=iso27001.CLAUSES,
        phases=phases,
        rows=rows,
        all_ids=all_ids,
        overall=percent_done(all_ids, rows),
        counts=counts,
        statuses=db.STATUSES,
        links=iso27001.LINKS,
        examples=iso27001.EXAMPLES,
        open_id=request.args.get("apen", ""),
    )


@app.route("/styringssystem/<item_id>", methods=["POST"])
def save_isms(item_id):
    if item_id not in iso27001.ITEM_IDS:
        abort(404)
    db.save_status("isms", item_id,
                   status=request.form.get("status", "ikke_startet"),
                   notes=request.form.get("notes", ""))
    return redirect(url_for("isms_page", apen=item_id) + "#c" + item_id)


# ---------- v5: NSM's measures (tiltak) ----------

@app.route("/tiltak")
def measures_page():
    rows = load_statuses("measures")
    groups = []
    for number, items in nsm_measures.by_group().items():
        label, name = nsm_measures.GROUPS[number]
        ids = [m["id"] for m in items]
        groups.append({"number": number, "label": label, "name": name, "measures": items,
                       "ids": ids, "percent": percent_done(ids, rows)})

    all_ids = [i for group in groups for i in group["ids"]]
    counts = {key: 0 for key in db.STATUSES}
    for measure_id in all_ids:
        counts[rows[measure_id]["status"] if measure_id in rows else "ikke_startet"] += 1

    return render_template(
        "measures.html",
        groups=groups,
        rows=rows,
        all_ids=all_ids,
        overall=percent_done(all_ids, rows),
        counts=counts,
        statuses=db.STATUSES,
        category_of=category_of(),
        # Principle number -> its page on nsm.no, which has the full text of each measure
        links={number: nsm_data.BASE + link for c in nsm_data.CATEGORIES
               for number, _title, link in c["principles"]},
        nsm_version=nsm_data.VERSION,
        sheet_url=nsm_measures.SOURCE_URL,
        open_id=request.args.get("apen", ""),
    )


@app.route("/tiltak/<measure_id>", methods=["POST"])
def save_measure(measure_id):
    if measure_id not in nsm_measures.TITLES:
        abort(404)
    db.save_status("measures", measure_id,
                   status=request.form.get("status", "ikke_startet"),
                   notes=request.form.get("notes", ""))
    # Go back to where the form was: the principle's category page, or the Tiltak page.
    if request.form.get("back") == "kategori":
        principle = nsm_measures.principle_of(measure_id)
        return redirect(url_for("category_page", category_id=category_of()[principle],
                                apen=measure_id) + "#t" + measure_id)
    return redirect(url_for("measures_page", apen=measure_id) + "#t" + measure_id)


# ---------- v6: report ----------

@app.route("/rapport")
def report():
    """One page with the state of everything, made to be printed or saved as PDF.

    In static mode every saved value is empty here, and report.js fills the
    page from the visitor's browser instead (like static-mode.js does elsewhere).
    """
    progress = load_progress()
    isms = load_statuses("isms")
    measure_rows = load_statuses("measures")
    soa = load_statuses("soa")

    principle_ids = [number for c in nsm_data.CATEGORIES for number, _t, _l in c["principles"]]
    clause_ids = [number for clause in iso27001.CLAUSES for number, _title in clause["items"]]
    groups = []
    for number, items in nsm_measures.by_group().items():
        label, name = nsm_measures.GROUPS[number]
        ids = [m["id"] for m in items]
        groups.append({"number": number, "label": label, "name": name, "measures": items,
                       "ids": ids, "percent": percent_done(ids, measure_rows)})

    soa_counts = {key: 0 for key in db.SOA_STATUSES}
    for control_id in iso27002.CONTROLS:
        soa_counts[soa[control_id]["status"] if control_id in soa else "ikke_vurdert"] += 1

    return render_template(
        "report.html",
        today=date.today().strftime("%d.%m.%Y"),
        categories=nsm_data.CATEGORIES,
        progress=progress,
        principle_ids=principle_ids,
        principles_percent=percent_done(principle_ids, progress),
        groups=groups,
        measure_rows=measure_rows,
        measure_ids=[i for g in groups for i in g["ids"]],
        measures_percent=percent_done([i for g in groups for i in g["ids"]], measure_rows),
        clauses=iso27001.CLAUSES,
        clause_ids=clause_ids,
        isms=isms,
        isms_percent=percent_done(clause_ids, isms),
        themes=iso27002.themes_with_controls(),
        soa=soa,
        soa_counts=soa_counts,
        statuses=db.STATUSES,
        soa_statuses=db.SOA_STATUSES,
        labels={**db.STATUSES, **db.SOA_STATUSES},   # every status label, for report.js
        incidents=incident_overview()["items"],
        incident_config=incidents.config_for_browser(),
        **risk_overview(),
    )


# ---------- v7: export and import ----------

# The two choices on the import form: what happens to the data that is already saved
IMPORT_MODES = {"erstatt": True, "sammen": False}    # value = replace?


def render_data_page(error=None, status=200):
    """The Data page. In static mode the counts are empty, and data.js fills them in."""
    if app.config["STATIC_SITE"]:
        saved = None
    else:
        saved = backup.counts(backup.export_data())
    page = render_template(
        "data.html",
        labels=backup.LABELS,
        saved=saved,
        error=error,
        # After an import: which choice was used, and how many risks and incidents were added
        # (only known values are shown)
        imported=request.args.get("importert") if request.args.get("importert") in IMPORT_MODES else "",
        added=request.args.get("nye", 0, type=int),
        added_incidents=request.args.get("nye_avvik", 0, type=int),
        rules=backup.rules_for_browser(),
    )
    return page, status


@app.route("/data")
def data_page():
    return render_data_page()


@app.route("/data/eksport")
def data_export():
    """Download all data as grunnmur-YYYY-MM-DD.json."""
    data = backup.export_data()
    body = json.dumps(data, ensure_ascii=False, indent=2)    # ensure_ascii=False keeps æ, ø and å readable
    return app.response_class(body, mimetype="application/json", headers={
        "Content-Disposition": f"attachment; filename=grunnmur-{data['exported']}.json"})


@app.route("/data/import", methods=["POST"])
def data_import():
    mode = request.form.get("mode", "")
    if mode not in IMPORT_MODES:
        return render_data_page("Velg om dataene skal erstattes eller slås sammen.", 400)
    upload = request.files.get("file")
    if not upload or not upload.filename:
        return render_data_page("Velg en fil å importere.", 400)
    try:
        parsed = json.loads(upload.read().decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return render_data_page("Filen er ikke gyldig JSON.", 400)

    data, error = backup.clean(parsed)
    if error:
        return render_data_page(error + " Ingenting er endret.", 400)
    added, added_incidents = db.import_all(data, replace=IMPORT_MODES[mode])
    # Post/Redirect/Get, like the other forms: a refresh will not import the file again
    return redirect(url_for("data_page", importert=mode, nye=added, nye_avvik=added_incidents))


@app.errorhandler(413)
def too_large(_error):
    """MAX_CONTENT_LENGTH was passed: show the Data page with a message instead of an error page."""
    return render_data_page("Filen er for stor (over 1 MB). Ingenting er endret.", 413)


@app.route("/om")
def about():
    return render_template("about.html", source_url=nsm_data.SOURCE_URL,
                           nsm_version=nsm_data.VERSION, roadmap=ROADMAP)


@app.route("/kategori/<category_id>")
def category_page(category_id):
    category = nsm_data.find_category(category_id)
    if category is None:
        abort(404)
    progress = load_progress()

    # Previous and next category, for the arrows at the bottom of the page.
    # The modulo (%) wraps around, so after category 4 comes category 1.
    categories = nsm_data.CATEGORIES
    index = categories.index(category)
    previous_category = categories[(index - 1) % len(categories)]
    next_category = categories[(index + 1) % len(categories)]
    measures = {number: nsm_measures.for_principle(number)
                for number, _title, _link in category["principles"]}
    measure_rows = load_statuses("measures")

    return render_template(
        "category.html",
        category=category,
        progress=progress,
        percent=category_progress(category, progress),
        counts=status_counts(category, progress),
        examples=examples.EXAMPLES,
        # v3: NSM's ISO 27002 controls per principle, e.g. {"2.3": ["5.21", "8.1", ...]}
        iso_controls={number: iso27002.controls_for_principle(number)
                      for number, _title, _link in category["principles"]},
        iso_titles=iso27002.CONTROLS,
        # v5: NSM's measures per principle, their saved status, and how many are done
        measures=measures,
        measure_rows=measure_rows,
        measure_done={number: sum(1 for m in items if m["id"] in measure_rows
                                  and measure_rows[m["id"]]["status"] == "implementert")
                      for number, items in measures.items()},
        previous_category=previous_category,
        next_category=next_category,
        statuses=db.STATUSES,
        base=nsm_data.BASE,
        # After saving, this principle is shown open so the user sees the result.
        open_id=request.args.get("apen", ""),
    )


@app.route("/prinsipp/<principle_id>", methods=["POST"])
def save_principle(principle_id):
    # Only accept principle numbers that actually exist in the NSM list.
    category = next(
        (c for c in nsm_data.CATEGORIES
         if any(p[0] == principle_id for p in c["principles"])),
        None,
    )
    if category is None:
        abort(404)

    db.save_progress(
        principle_id,
        status=request.form.get("status", "ikke_startet"),
        notes=request.form.get("notes", ""),
        iso_ref=request.form.get("iso_ref", ""),
        gdpr="gdpr" in request.form,  # a checkbox is only sent when it is ticked
    )
    # Post/Redirect/Get: redirecting after a POST stops the browser from
    # resubmitting the form if the user refreshes the page.
    return redirect(url_for("category_page", category_id=category["id"],
                            apen=principle_id) + "#p" + principle_id)


# ---------- v2: risk register ----------

def render_risk_form(risk, risk_id=None, error=None):
    """Show the new/edit form. risk_id is None for a new risk."""
    return render_template(
        "risk_form.html",
        risk=risk,
        risk_id=risk_id,
        error=error,
        categories=nsm_data.CATEGORIES,
        likelihood=risks.LIKELIHOOD,
        impact=risks.IMPACT,
        treatments=risks.TREATMENTS,
        statuses=risks.STATUSES,
        example=risks.EXAMPLE,
        risk_config=risks.config_for_browser(),
        # v5: NSM's measures per principle, most urgent first. The form shows the
        # list for the chosen principle as suggestions (risk-tools.js swaps it).
        suggestions={number: nsm_measures.suggestions(number) for number in nsm_data.PRINCIPLE_IDS},
    )


def risk_overview():
    """Everything the risk list shows, also used by the report (v6)."""
    # Same rule as load_progress(): the public build never contains my own data.
    rows = [] if app.config["STATIC_SITE"] else db.get_all_risks()
    items = sorted((risks.enrich(row) for row in rows), key=risks.sort_key)

    # How many risks there are per level, for the summary at the top.
    level_counts = {key: 0 for key, _label, _lowest in risks.LEVELS}
    for item in items:
        level_counts[item["level"]] += 1

    # An empty example row. On GitHub Pages, static-risks.js copies it
    # for every risk saved in the browser, so both versions share one layout.
    placeholder = risks.enrich({**risks.DEFAULTS, "id": "", "title": ""})

    return dict(
        items=items,
        levels=risks.LEVELS,
        level_counts=level_counts,
        # v5: heat maps before and after the measures, and how many open risks
        # still lack a residual assessment (they are not in the "after" map)
        map_before=risks.heat_map(items),
        map_after=risks.heat_map(items, residual=True),
        missing_residual=sum(1 for item in items
                             if item["status"] != "lukket" and item["residual_score"] is None),
        placeholder=placeholder,
        risk_config=risks.config_for_browser(),
    )


@app.route("/risikoer")
def risk_list():
    return render_template("risks.html", **risk_overview())


@app.route("/risikoer/ny", methods=["GET", "POST"])
def risk_new():
    if request.method == "POST":
        data, error = risks.read_form(request.form)
        if error:
            return render_risk_form(data, error=error), 400
        db.add_risk(data)
        return redirect(url_for("risk_list"))
    return render_risk_form(dict(risks.DEFAULTS))


@app.route("/risikoer/<int:risk_id>", methods=["GET", "POST"])
def risk_edit(risk_id):
    risk = db.get_risk(risk_id)
    if risk is None:
        abort(404)
    if request.method == "POST":
        data, error = risks.read_form(request.form)
        if error:
            return render_risk_form(data, risk_id, error), 400
        db.update_risk(risk_id, data)
        return redirect(url_for("risk_list"))
    return render_risk_form(risk, risk_id)


@app.route("/risikoer/<int:risk_id>/slett", methods=["POST"])
def risk_delete(risk_id):
    db.delete_risk(risk_id)
    return redirect(url_for("risk_list"))


# ---------- v8: incident log ----------

def incident_overview():
    """Every incident with its labels, sorted: open first, then newest. Empty in static mode."""
    if app.config["STATIC_SITE"]:
        return {"items": [], "risk_titles": {}}
    risk_titles = {risk["id"]: risk["title"] for risk in db.get_all_risks()}
    items = [incidents.enrich(row, risk_titles) for row in db.get_all_incidents()]
    return {"items": sorted(items, key=incidents.sort_key), "risk_titles": risk_titles}


def render_incident_form(incident, incident_id=None, error=None):
    """Show the new/edit form. incident_id is None for a new incident."""
    return render_template(
        "incident_form.html",
        incident=incident,
        incident_id=incident_id,
        error=error,
        categories=nsm_data.CATEGORIES,
        severities=incidents.SEVERITIES,
        statuses=incidents.STATUSES,
        example=incidents.EXAMPLE,
        gdpr_note=incidents.GDPR_NOTE,
        # The risks to link to, by title. On GitHub Pages static-incidents.js fills the menu.
        risk_titles=incident_overview()["risk_titles"],
    )


@app.route("/avvik")
def incident_list():
    return render_template("incidents.html", items=incident_overview()["items"],
                           gdpr_note=incidents.GDPR_NOTE,
                           incident_config=incidents.config_for_browser())


@app.route("/avvik/ny", methods=["GET", "POST"])
def incident_new():
    if request.method == "POST":
        data, error = incidents.read_form(request.form, set(incident_overview()["risk_titles"]))
        if error:
            return render_incident_form(data, error=error), 400
        db.add_incident(data)
        return redirect(url_for("incident_list"))
    # A new incident starts with today's date
    return render_incident_form({**incidents.DEFAULTS, "date": date.today().isoformat()})


@app.route("/avvik/<int:incident_id>", methods=["GET", "POST"])
def incident_edit(incident_id):
    incident = db.get_incident(incident_id)
    if incident is None:
        abort(404)
    if request.method == "POST":
        data, error = incidents.read_form(request.form, set(incident_overview()["risk_titles"]))
        if error:
            return render_incident_form(data, incident_id, error), 400
        db.update_incident(incident_id, data)
        return redirect(url_for("incident_list"))
    return render_incident_form(incident, incident_id)


@app.route("/avvik/<int:incident_id>/slett", methods=["POST"])
def incident_delete(incident_id):
    db.delete_incident(incident_id)
    return redirect(url_for("incident_list"))


if __name__ == "__main__":
    db.init_db()
    # 127.0.0.1 = only reachable from this computer. debug=True reloads on code changes.
    app.run(host="127.0.0.1", port=5050, debug=True)
