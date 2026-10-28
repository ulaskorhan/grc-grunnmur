# Grunnmur

A small personal GRC (Governance, Risk and Compliance) app, in Norwegian, built on
[NSM Grunnprinsipper for IKT-sikkerhet v2.1](https://nsm.no/regelverk-og-hjelp/rad-og-anbefalinger/grunnprinsipper-for-ikt-sikkerhet/).

It starts simple and grows one version at a time:

| Version | Content | Status |
|---------|---------|--------|
| v1 | Control tracker: 4 categories, 21 principles, status, notes, ISO 27001 reference, GDPR tag | Done |
| v2 | Risk register (likelihood × impact, treatment, link to a principle) | Planned |
| v3 | NSM measures (tiltak) under each principle, plus a risk heatmap | Planned |
| v4 | Export, English/Norwegian README, screenshots | Planned |

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then open <http://127.0.0.1:5050>.

## Public version (GitHub Pages)

Live: <https://ulaskorhan.github.io/grc-grunnmur/>

GitHub Pages can only host static files, so `build.py` renders the same Flask
templates into `docs/` with empty progress. On that version, `static/static-mode.js`
saves each visitor's answers in their own browser (localStorage). Nothing is sent
to a server, and my local database is never part of the build.

After changing templates, styles or data, rebuild and commit `docs/`:

```bash
.venv/bin/python build.py
git add docs && git commit -m "Rebuild GitHub Pages site"
```

## Files

- `app.py`: Flask routes (homepage, category page, saving a principle)
- `db.py`: SQLite setup plus reading and writing progress
- `nsm_data.py`: the 4 categories and 21 principles, copied from NSM's website
- `build.py`: builds the static GitHub Pages version into `docs/`
- `static/static-mode.js`: browser storage for the GitHub Pages version
- `examples.py`: one home lab example per principle, behind the "Eksempel" button (written for this app, not NSM text)
- `templates/`: HTML pages (Jinja)
- `static/style.css`: the minimalist styling

The ISO 27001 references are entered by the user. No ISO text is included.
