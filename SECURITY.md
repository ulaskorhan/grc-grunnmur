# Security considerations

*Last reviewed: 24.11.2026*

A GRC tool holds the most sensitive information an organisation has: open weaknesses,
missing controls, risk assessments and who is responsible for what. In the wrong hands
it is a map of how to attack you. A GRC tool built quickly, or with an AI coding
assistant, without enough attention to architecture and secure development is a real
risk, and one that is rarely discussed.

This file is how Grunnmur takes that risk seriously. It says what the tool is for, how
data flows, what is protected, and what is **not**, so anyone can judge the risk before
using it.

## In short

- **Grunnmur is a learning and portfolio project.** It is for a home lab, a small
  personal setup, or as a template for structuring the work.
- **Do not enter real sensitive information from an organisation** (real vulnerabilities,
  network details, names, incidents) unless your organisation has assessed and accepted
  the risk, the same as for any other tool.
- **No server ever receives your data.** There are no accounts, no database in the cloud,
  no analytics and no third-party scripts.
- **The code was written with an AI coding assistant (Claude Code)** under my direction.
  Every change was reviewed, tested and committed in small steps; the history is public
  in this repository. The controls below are there because AI-written code needs the same
  scrutiny as any other code, and arguably more.

## Architecture and data flow

There are two versions, built from the same code.

| | Public version (GitHub Pages) | Local version (Flask) |
|---|---|---|
| Where it runs | Static files served by GitHub | `python app.py` on your own computer |
| Where data is stored | `localStorage` in the visitor's own browser | `grunnmur.db` (SQLite) on your disk |
| Who can reach it | Anyone can load the pages; only you see your data | Only `127.0.0.1` (this computer) |
| Data sent over the network | None. The pages make no requests with your data | None. Browser and server are on the same machine |
| Accounts / passwords | None | None |

The public build is made by `build.py` with an empty database, and a test checks that
no local data (risks, notes, incidents) can ever end up in the published files.

## Threats and controls

| Threat | Control | Tested by |
|---|---|---|
| A central database is breached and everyone's data leaks | There is no central database. Data stays on each user's device | Architecture |
| My local data is published by mistake | The public build never reads the database; a test renders every page with secret markers and fails if they appear | `tests/test_pages.py` |
| Text a user enters runs as code (XSS) | Jinja escapes all output; the browser scripts use `textContent`, never `innerHTML` | `tests/test_pages.py` |
| An escaping bug slips through anyway | **Content security policy** in every page: scripts only from the site itself, no inline code, no third-party sources, forms only to the site itself, no network requests from scripts | `tests/test_security.py` |
| A third-party script or CDN is compromised (supply chain) | No external scripts, fonts, analytics or trackers are loaded | Architecture and CSP |
| Another website makes your browser post a form to the local app (CSRF) | The local app refuses POST requests whose `Origin` or `Sec-Fetch-Site` header says they come from another site | `tests/test_security.py` |
| A web page reaches the local app under its own domain name (DNS rebinding) | The local app only answers requests addressed to `127.0.0.1` or `localhost` (`TRUSTED_HOSTS`) | `tests/test_security.py` |
| The app is shown inside another site to trick clicks (clickjacking) | `X-Frame-Options: DENY` on the local app | `tests/test_security.py` |
| Flask's debug console is reached and used to run code | Debug mode is off by default; it is only on with `GRUNNMUR_DEBUG=1` while developing | `app.py` |
| The local app is reached from the network | It listens on `127.0.0.1` only | `app.py` |
| A huge or malformed import file | Size limit before reading; every field is checked before anything is saved | `tests/test_backup.py` |

## What is not protected (accepted risks)

These are known and accepted for a learning tool. They would need to be solved before
using Grunnmur for real data in an organisation.

- **Data is not encrypted on the device.** `localStorage` and `grunnmur.db` are plain
  text. Anyone with access to your user account, your device or a backup of it can read
  them.
- **Browser extensions can read the page.** An extension with access to all sites can
  read what the public version shows and stores.
- **The export file is plain JSON.** Treat it as a sensitive document: store it
  encrypted, and do not email it or put it in a shared folder.
- **A shared or public computer keeps the data** until "Slett mine data" is used or the
  browser data is cleared.
- **No login, roles or audit log.** Anyone who can use your browser or computer can
  change everything, and there is no record of who did what.
- **Inline `style=""` attributes are allowed by the content security policy**, because
  a few elements set a CSS variable that way. Styles cannot run code, so the risk is low.
- **GitHub Pages cannot send security headers.** The policy is in a `<meta>` tag instead,
  which covers scripts but not `frame-ancestors`; the public pages could be framed.
  There is no data on the server to steal that way.
- **The automatic cyber-level check has write access to this repository**
  (`contents: write` in `.github/workflows/check-cyber-level.yml`), to commit the new
  date. GitHub Actions are pinned to major versions (`@v4`), not to commit hashes.
- **The app has not had an independent security review or penetration test.**

## Advice if you use it

1. Use it for learning, a home lab, or as a template, not as a system of record for an
   organisation.
2. Use your own device and browser profile, not a shared one.
3. Store exported files encrypted, and delete old ones.
4. If you run the local version, keep it on `127.0.0.1` and do not enable debug mode
   outside development.

## Reporting a security problem

Please do not open a public issue with details of a vulnerability. Use GitHub's private
reporting instead: the **Security** tab of this repository → **Report a vulnerability**.
