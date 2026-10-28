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

Then open <http://127.0.0.1:5000>.

## Files

- `app.py`: Flask routes (homepage, category page, saving a principle)
- `db.py`: SQLite setup plus reading and writing progress
- `nsm_data.py`: the 4 categories and 21 principles, copied from NSM's website
- `templates/`: HTML pages (Jinja)
- `static/style.css`: the minimalist styling

The ISO 27001 references are entered by the user. No ISO text is included.
