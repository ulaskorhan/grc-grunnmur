# Grunnmur

**English** · [Norsk](README.no.md)

A small personal GRC (Governance, Risk and Compliance) app, in Norwegian, built on
[NSM's basic principles for ICT security, v2.1](https://nsm.no/regelverk-og-hjelp/rad-og-anbefalinger/grunnprinsipper-for-ikt-sikkerhet/)
(NSM Grunnprinsipper for IKT-sikkerhet), with links to ISO/IEC 27001, ISO/IEC 27002 and GDPR.

Live: <https://ulaskorhan.github.io/grc-grunnmur/>

## Why

NSM (the Norwegian National Security Authority) says *what* an organisation should do:
21 principles with 118 measures. NSM's own self-assessment, Cybersjekk, gives a quick
overview. What is left after that is the follow-up work: who does what, what is done,
which risks remain, and when it should be reviewed again. Grunnmur is a small tool for
that follow-up, for a small business or a home lab. ISO 27001 adds the management
system around it (how security is governed), so the app connects the two.

## What it does

The app was built in seven versions:

| Version | Content |
|---------|---------|
| v1 | The 21 principles in 4 categories, each with status, notes, ISO 27001 reference, GDPR tag and an example |
| v2 | Risk register: likelihood × impact (1–5), treatment, review date, linked to a principle (ISO 27001 6.1) |
| v3 | The 93 ISO/IEC 27002:2022 controls in 4 themes, with NSM's own mapping to the principles |
| v4 | ISO 27001 clauses 4–10 in the Plan-Do-Check-Act cycle, plus a statement of applicability (SoA) for the 93 controls |
| v5 | NSM's 118 measures with status, sorted by NSM's priority groups; residual risk and heat maps before and after measures; NSM measures suggested on the risk form |
| v6 | A print-friendly report of everything on one page (print or save as PDF from the browser), and this README in English and Norwegian |
| v7 | Export and import of all data as one JSON file, in both versions, so data can be backed up or moved between the local and the public version |

A thin banner at the top of every page shows NSM's national cyber risk level
(nasjonalt cyberrisikonivå), with the date NSM set it and the date it was last checked.
The homepage lists open risks whose review is overdue or due within 30 days.

## How it works

```
                    templates/ (Jinja) + static/ (CSS, JS)
                                  │
            ┌─────────────────────┴─────────────────────┐
   Local:   Flask (app.py) + SQLite (db.py)     build.py renders every page
            data saved in grunnmur.db           with STATIC_SITE on, into docs/
                                                         │
                                       GitHub Pages: static HTML, and the
                                       visitor's data in their own browser
                                       (localStorage, static-mode.js)
```

- **Locally** the app is a normal Flask app with an SQLite database.
- **Publicly** GitHub Pages can only host static files. `build.py` asks Flask for every
  page and saves the HTML to `docs/`, with empty data. In that version small scripts
  save each visitor's answers in their own browser. Nothing is sent to a server, and
  my local database is never part of the build.
- The same templates are used in both versions, so they look and work the same.
- Export and import use one JSON format in both versions (described in `backup.py`).
  An imported file is checked completely before anything is saved, with the same rules
  as the forms. If one value is wrong, nothing changes. On import the user chooses to
  replace everything or to merge; a merge never adds a risk that is already there.
- Accessibility: every page was checked with axe-core against WCAG 2.2 AA, in light and dark
  mode and with data in every state. There is a skip link, visible keyboard focus, text
  contrast of at least 4.5:1, and no links inside the clickable rows.
- Risk levels are calculated in Python (`risks.py`). The same rules are sent to the
  browser as JSON, so the static version calculates exactly the same.

## Sources and honesty

- **NSM:** the principle titles and the measure headings are copied exactly from NSM,
  with source and date. The full text stays on nsm.no, and every principle and measure
  links there.
- **NSM ↔ ISO 27002 mapping and priorities:** NSM's own, from NSM's spreadsheet of
  measures. Only numbers are copied. NSM notes that the mapping is a judgement and
  rarely 1:1.
- **ISO:** the standards are copyrighted, so no ISO text is included. Only clause and
  control numbers are used, with short titles in my own words.
- **Examples:** written for this app, not taken from NSM or ISO.
- **Cyber risk level:** copied by hand from NSM's announcement into `cyber_level.py`.
  NSM has no open API. Every third day a GitHub Action (`check_cyber_level.py`) reads
  NSM's news feed: if there is no new announcement it updates the "last checked" date
  and rebuilds the site; if there is one, it opens an issue and the level is changed by
  hand after reading NSM's text. The level is never guessed from a headline.

## Limitations

- Not an official service, and not connected to NSM. It does not replace NSM's advice,
  Cybersjekk or an audit.
- One user, no login. It is meant for one person or a small team on one machine.
- On the public version the data lives only in that browser. Clearing the browser's
  data deletes it, so export a file now and then as a backup.
- The exported file holds your notes as plain text. It is not encrypted.

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then open <http://127.0.0.1:5050>.

## Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
```

The tests in `tests/` check the risk rules and reminders, export and import, that every
page loads, that user text is escaped, that the public build never contains local data,
and the cyber level check (without going online). Each test gets its own empty database.
A GitHub Action (`.github/workflows/tests.yml`) runs them on every push.

## Building the public version

After changing templates, styles or data, rebuild and commit `docs/`:

```bash
.venv/bin/python build.py
git add docs && git commit -m "Rebuild GitHub Pages site"
```

The check of the cyber risk level also commits to `main`, so run `git pull` before pushing.

For a local preview of the build: `BASE_PATH= .venv/bin/python build.py`, then
`python3 -m http.server 8000 --directory docs`.

## Files

- `app.py`: Flask routes for every page
- `db.py`: SQLite tables and reading and writing (progress, risks, clauses, SoA, measures), and saving an import
- `backup.py`: the JSON file format, export, and the checks on an imported file
- `nsm_data.py`: NSM's 4 categories and 21 principles
- `nsm_measures.py`: NSM's 118 measure headings and priority groups
- `nsm_iso_mapping.py`: NSM's mapping from measures to ISO 27002 controls (numbers only)
- `iso27002.py`: the 93 controls with short titles in my own words
- `iso27001.py`: clauses 4–10, PDCA phases and one example per requirement
- `risks.py`: risk scales, levels, validation, residual risk and heat maps
- `examples.py`: one home lab example per principle
- `cyber_level.py`: NSM's national cyber risk level (updated by hand)
- `check_cyber_level.py`, `.github/workflows/check-cyber-level.yml`: the check of NSM's news feed every third day
- `build.py`: builds the static version into `docs/`
- `tests/`: the pytest tests; `requirements-dev.txt` adds pytest
- `templates/`: the HTML pages (Jinja)
- `static/style.css`: the styling, mobile first, with dark mode and print styles
- `static/static-mode.js`: browser storage for principles, measures, clauses and SoA (public version)
- `static/static-risks.js`: the risk register in the browser (public version)
- `static/risk-tools.js`: heat map filter and NSM suggestions (both versions)
- `static/report.js`: fills the report from the browser (public version)
- `static/reminders.js`: the review reminders on the homepage (public version)
- `static/data.js`: export and import in the browser (public version), and the confirmation before replacing (both)
- `static/favicon.svg`, `static/og-image.png`: the tab icon and the picture shown when the link is shared

Built with Python, Flask and SQLite. No JavaScript framework.
