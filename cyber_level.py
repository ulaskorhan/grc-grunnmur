"""NSM's national cyber risk level (nasjonalt cyberrisikonivå), shown at the top of every page.

This is NOT live data. NSM has no open API for the level, and GitHub Pages cannot
fetch nsm.no from the browser. So the value is copied by hand from NSM's own
announcement, together with the date and a link, and must be updated when NSM
changes the level. CHECKED says when I last compared it with nsm.no.
"""

# NSM's five levels, lowest first. NSM describes MODERAT as the normal state.
SCALE = ["Svært lavt", "Lavt", "Moderat", "Høyt", "Ekstremt høyt"]

CURRENT = "Høyt"                  # must be one of SCALE
SET_ON = "27.10.2026"             # the date NSM raised the level
CHECKED = "29.10.2026"            # the date I last checked nsm.no
SOURCE_URL = "https://nsm.no/aktuelt/nsm-hever-det-nasjonale-cyberrisikonivaet-til-hoyt"


def for_template():
    """Everything base.html needs to draw the banner and its 5-step scale."""
    position = SCALE.index(CURRENT)   # fails loudly if CURRENT is misspelt
    return {
        "scale": SCALE,
        "current": CURRENT,
        "position": position,
        # Above MODERAT (the normal state) the banner uses warning colours.
        "elevated": position > SCALE.index("Moderat"),
        "set_on": SET_ON,
        "checked": CHECKED,
        "source_url": SOURCE_URL,
    }
