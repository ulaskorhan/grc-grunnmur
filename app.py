"""Grunnmur: a small personal GRC app built on NSM Grunnprinsipper for IKT-sikkerhet.

Run with:  .venv/bin/python app.py   and open http://127.0.0.1:5050

Pages:
  /                     homepage: the 4 categories with progress, plus the roadmap
  /kategori/<id>        one category: its principles, collapsed until clicked
  /prinsipp/<nr> (POST) saves the form for one principle
"""

from flask import Flask, abort, redirect, render_template, request, url_for

import db
import examples
import nsm_data

app = Flask(__name__)
# Tell browsers to re-check style.css on every load, so design changes show up
# immediately instead of an old cached version being used.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
# STATIC_SITE is switched on by build.py when it makes the GitHub Pages version.
# In that mode no data is read from the database, and the browser saves progress instead.
app.config["STATIC_SITE"] = False

# How much each status counts towards the progress score (0-100 %).
SCORE = {"ikke_startet": 0, "delvis": 0.5, "implementert": 1}

# The version plan shown on the homepage, so users know the app will grow.
ROADMAP = [
    (1, "Grunnprinsipper", "Status, notater, ISO-referanse og personvern per prinsipp"),
    (2, "Risikoregister", "Sannsynlighet × konsekvens, behandling og kobling til NSM og ISO 27001 6.1"),
    (3, "ISO 27001 styringssystem", "Kapittel 4–10 og kobling mellom NSM-prinsipper og Annex A"),
    (4, "Tiltak og varmekart", "NSMs tiltak under hvert prinsipp og et risikovarmekart"),
    (5, "Eksport og portefølje", "Eksport av data og ferdig presentasjon"),
]
CURRENT_VERSION = 1


@app.context_processor
def add_static_flag():
    """Make the variable "static_site" available in every template."""
    return {"static_site": app.config["STATIC_SITE"]}


def load_progress():
    """Read saved progress, except in static mode.

    The public GitHub Pages build must never contain my own local data,
    so it always starts empty. Visitors' progress is saved in their own browser.
    """
    if app.config["STATIC_SITE"]:
        return {}
    return db.get_all_progress()


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
    return render_template(
        "home.html",
        cards=cards,
        overall=overall,
        implemented=implemented,
        total=total,
        roadmap=ROADMAP,
        current_version=CURRENT_VERSION,
        source_url=nsm_data.SOURCE_URL,
        nsm_version=nsm_data.VERSION,
    )


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

    return render_template(
        "category.html",
        category=category,
        progress=progress,
        percent=category_progress(category, progress),
        counts=status_counts(category, progress),
        examples=examples.EXAMPLES,
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


if __name__ == "__main__":
    db.init_db()
    # 127.0.0.1 = only reachable from this computer. debug=True reloads on code changes.
    app.run(host="127.0.0.1", port=5050, debug=True)
