"""Check NSM's news feed for a new announcement about the national cyber risk level.

Run by .github/workflows/check-cyber-level.yml every third day, or by hand:
    .venv/bin/python check_cyber_level.py

Two outcomes:
  - No new announcement: CHECKED in cyber_level.py is set to today's date,
    so the site honestly shows when the level was last compared with NSM.
  - A new announcement: nothing is changed. Its title and link are written to
    a file (the first argument, if given), and the workflow opens an issue.
    The level is then updated by hand after reading NSM's own text.

The level itself is never guessed from a headline: a wrong level on a security
site is worse than one that is a few days late.
"""

import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import cyber_level

FEED_URL = "https://nsm.no/rss/nyheter-fra-nsm/"
KEYWORD = "cyberrisikonivå"          # NSM's announcements have this word in the title
OSLO = ZoneInfo("Europe/Oslo")


def fetch_items():
    """The news items in NSM's RSS feed, as dicts with title, link and date."""
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": "grunnmur-check (github.com/ulaskorhan/grc-grunnmur)"})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    items = [{"title": item.findtext("title", "").strip(),
              "link": item.findtext("link", "").strip(),
              "date": parsedate_to_datetime(item.findtext("pubDate"))}
             for item in root.iter("item")]
    # An empty feed means something is wrong, so stop instead of claiming "checked"
    if not items:
        raise SystemExit("NSM's feed had no news items. Has the feed changed?")
    return items


def new_announcements(items):
    """Items about the cyber risk level that are newer than the one the site shows."""
    set_on = datetime.strptime(cyber_level.SET_ON, "%d.%m.%Y").date()
    known = cyber_level.SOURCE_URL.rstrip("/")
    return [item for item in items
            if KEYWORD in item["title"].lower()
            and item["link"].rstrip("/") != known
            and item["date"].astimezone(OSLO).date() >= set_on]


def mark_checked(day):
    """Write the date into the CHECKED line of cyber_level.py."""
    path = Path(cyber_level.__file__)
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(r'^CHECKED = "[^"]*"', f'CHECKED = "{day}"', text, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit("Could not find the CHECKED line in cyber_level.py")
    path.write_text(text, encoding="utf-8")


def main():
    found = new_announcements(fetch_items())
    if found:
        lines = ["NSMs nyhetsfeed har en ny sak om det nasjonale cyberrisikonivået:", ""]
        lines += [f"- [{item['title']}]({item['link']}) ({item['date'].astimezone(OSLO):%d.%m.%Y})" for item in found]
        lines += ["", "Les saken, og oppdater `CURRENT`, `SET_ON`, `CHECKED` og `SOURCE_URL` "
                      "i `cyber_level.py` for hånd. Bygg deretter siden på nytt."]
        print("\n".join(lines))
        if len(sys.argv) > 1:
            Path(sys.argv[1]).write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    today = datetime.now(OSLO).strftime("%d.%m.%Y")
    mark_checked(today)
    print(f"No new announcement. CHECKED set to {today}.")


if __name__ == "__main__":
    main()
