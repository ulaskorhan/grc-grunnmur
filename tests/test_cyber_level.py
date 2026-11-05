"""The check of NSM's news feed (check_cyber_level.py), without going online."""

from datetime import datetime, timezone

import check_cyber_level as check
import cyber_level


def item(title, link, day):
    return {"title": title, "link": link, "date": datetime(*day, 10, tzinfo=timezone.utc)}


def test_only_new_announcements_about_the_level_count():
    items = [
        item("NSM hever det nasjonale cyberrisikonivået til HØYT", cyber_level.SOURCE_URL, (2026, 10, 27)),
        item("Ber befolkningen forberede seg på cyberangrep", "https://nsm.no/a", (2026, 10, 29)),
        item("Gammel sak om cyberrisikonivået", "https://nsm.no/b", (2026, 1, 1)),
        item("NSM senker cyberrisikonivået til MODERAT", "https://nsm.no/c", (2026, 12, 1)),
    ]
    found = check.new_announcements(items)
    assert [i["link"] for i in found] == ["https://nsm.no/c"]


def test_current_level_is_on_nsms_scale():
    assert cyber_level.CURRENT in cyber_level.SCALE
    datetime.strptime(cyber_level.SET_ON, "%d.%m.%Y")
    datetime.strptime(cyber_level.CHECKED, "%d.%m.%Y")
