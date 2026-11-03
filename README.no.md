# Grunnmur

[English](README.md) · **Norsk**

En liten personlig GRC-app (styring, risiko og etterlevelse) på norsk, bygget på
[NSMs grunnprinsipper for IKT-sikkerhet v2.1](https://nsm.no/regelverk-og-hjelp/rad-og-anbefalinger/grunnprinsipper-for-ikt-sikkerhet/),
med kobling til ISO/IEC 27001, ISO/IEC 27002 og GDPR.

Live: <https://ulaskorhan.github.io/grc-grunnmur/>

## Hvorfor

NSM sier *hva* en virksomhet bør gjøre: 21 prinsipper med 118 tiltak. NSMs egen
selvevaluering, Cybersjekk, gir en rask oversikt. Det som gjenstår etterpå, er
oppfølgingen: hvem gjør hva, hva er gjort, hvilke risikoer gjenstår, og når skal det
vurderes på nytt? Grunnmur er et lite verktøy for den oppfølgingen, for en liten
virksomhet eller en hjemmelab. ISO 27001 legger styringssystemet rundt (hvordan
sikkerhet styres), så appen kobler de to.

## Hva den gjør

Appen er bygget i sju versjoner:

| Versjon | Innhold |
|---------|---------|
| v1 | De 21 prinsippene i 4 kategorier, hver med status, notater, ISO 27001-referanse, personvernmerke og et eksempel |
| v2 | Risikoregister: sannsynlighet × konsekvens (1–5), behandling og neste gjennomgang, koblet til et prinsipp (ISO 27001 6.1) |
| v3 | De 93 kontrollene i ISO/IEC 27002:2022 i 4 temaer, med NSMs egen kobling til prinsippene |
| v4 | ISO 27001 kapittel 4–10 i PDCA-sirkelen, og en anvendelseserklæring (SoA) for de 93 kontrollene |
| v5 | NSMs 118 tiltak med status, sortert etter NSMs prioriteringsgrupper; restrisiko og varmekart før og etter tiltak; NSMs tiltak som forslag i risikoskjemaet |
| v6 | En utskriftsvennlig rapport med alt på én side (skriv ut eller lagre som PDF fra nettleseren), og denne README-en på engelsk og norsk |
| v7 | Eksport og import av alle data som én JSON-fil, i begge versjonene, som backup eller for å flytte data mellom lokal og offentlig versjon |

Et tynt banner øverst på hver side viser NSMs nasjonale cyberrisikonivå, med dato og kilde.

## Slik virker den

```
                    templates/ (Jinja) + static/ (CSS, JS)
                                  │
            ┌─────────────────────┴─────────────────────┐
   Lokalt:  Flask (app.py) + SQLite (db.py)     build.py lager hver side
            data lagres i grunnmur.db           med STATIC_SITE på, i docs/
                                                         │
                                       GitHub Pages: statisk HTML, og
                                       besøkendes data i egen nettleser
                                       (localStorage, static-mode.js)
```

- **Lokalt** er appen en vanlig Flask-app med en SQLite-database.
- **Offentlig** kan GitHub Pages bare vise statiske filer. `build.py` henter hver side
  fra Flask og lagrer HTML-en i `docs/`, uten data. I den versjonen lagrer små skript
  hver besøkendes svar i deres egen nettleser. Ingenting sendes til en server, og min
  lokale database kommer aldri med i byggingen.
- Begge versjonene bruker de samme malene, så de ser like ut og virker likt.
- Eksport og import bruker samme JSON-format i begge versjonene (beskrevet i `backup.py`).
  En importert fil sjekkes helt før noe lagres, med de samme reglene som skjemaene.
  Er én verdi feil, endres ingenting. Ved import velger brukeren å erstatte alt eller
  slå sammen. Sammenslåing legger aldri til en risiko som finnes fra før.
- Risikonivåene regnes ut i Python (`risks.py`). De samme reglene sendes til
  nettleseren som JSON, så den statiske versjonen regner helt likt.

## Kilder og ærlighet

- **NSM:** prinsipptitlene og tiltaksoverskriftene er kopiert ordrett fra NSM, med kilde
  og dato. Den fulle teksten finnes hos NSM, og hvert prinsipp og tiltak lenker dit.
- **Koblingen NSM ↔ ISO 27002 og prioriteringen:** er NSMs egne, fra NSMs regneark med
  tiltak. Bare numrene er kopiert. NSM påpeker at koblingen bygger på skjønn og sjelden er 1:1.
- **ISO:** standardene er opphavsrettsbeskyttet, så ingen ISO-tekst er gjengitt. Appen
  bruker bare kapittel- og kontrollnumre, med korte titler skrevet med egne ord.
- **Eksempler:** skrevet for denne appen, ikke hentet fra NSM eller ISO.
- **Cyberrisikonivå:** skrevet inn for hånd fra NSMs kunngjøring i `cyber_level.py`.
  NSM har ikke et åpent API, så nivået må oppdateres for hånd når NSM endrer det.

## Begrensninger

- Ikke en offisiell tjeneste, og ikke tilknyttet NSM. Den erstatter ikke NSMs råd,
  Cybersjekk eller en revisjon.
- Én bruker, ingen innlogging. Den er laget for én person eller et lite team på én maskin.
- I den offentlige versjonen finnes dataene bare i den nettleseren. Sletter du nettleserens
  data, forsvinner de, så eksporter en fil av og til som backup.
- Den eksporterte filen har notatene dine som vanlig tekst. Den er ikke kryptert.

## Kjøre den

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Åpne deretter <http://127.0.0.1:5050>.

## Bygge den offentlige versjonen

Etter endringer i maler, stil eller data: bygg på nytt og commit `docs/`:

```bash
.venv/bin/python build.py
git add docs && git commit -m "Rebuild GitHub Pages site"
```

For å se byggingen lokalt: `BASE_PATH= .venv/bin/python build.py`, og deretter
`python3 -m http.server 8000 --directory docs`.

## Filer

- `app.py`: Flask-rutene for alle sidene
- `db.py`: SQLite-tabeller, lesing og lagring (fremdrift, risikoer, kapittelkrav, SoA, tiltak), og lagring av en import
- `backup.py`: JSON-formatet, eksport og sjekken av en importert fil
- `nsm_data.py`: NSMs 4 kategorier og 21 prinsipper
- `nsm_measures.py`: NSMs 118 tiltaksoverskrifter og prioriteringsgrupper
- `nsm_iso_mapping.py`: NSMs kobling fra tiltak til ISO 27002-kontroller (bare numre)
- `iso27002.py`: de 93 kontrollene med korte titler med egne ord
- `iso27001.py`: kapittel 4–10, PDCA-faser og ett eksempel per krav
- `risks.py`: risikoskalaer, nivåer, validering, restrisiko og varmekart
- `examples.py`: ett hjemmelab-eksempel per prinsipp
- `cyber_level.py`: NSMs nasjonale cyberrisikonivå (oppdateres for hånd)
- `build.py`: bygger den statiske versjonen i `docs/`
- `templates/`: HTML-sidene (Jinja)
- `static/style.css`: stilen, mobil først, med mørk modus og utskriftsstil
- `static/static-mode.js`: lagring i nettleseren for prinsipper, tiltak, kapittelkrav og SoA (offentlig versjon)
- `static/static-risks.js`: risikoregisteret i nettleseren (offentlig versjon)
- `static/risk-tools.js`: filter i varmekartet og forslag fra NSM (begge versjoner)
- `static/report.js`: fyller rapporten fra nettleseren (offentlig versjon)
- `static/data.js`: eksport og import i nettleseren (offentlig versjon), og bekreftelsen før erstatning (begge)

Bygget med Python, Flask og SQLite. Uten JavaScript-rammeverk.
