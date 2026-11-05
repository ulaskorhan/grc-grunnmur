"""The risk rules in risks.py: levels, form checks and review reminders."""

from datetime import date

import pytest

import risks
from conftest import RISK_FORM

TODAY = date(2026, 11, 5)


@pytest.mark.parametrize("score, level", [
    (1, "lav"), (4, "lav"), (5, "middels"), (9, "middels"),
    (10, "hoy"), (16, "hoy"), (20, "kritisk"), (25, "kritisk"),
])
def test_risk_level_boundaries(score, level):
    assert risks.risk_level(score)[0] == level


def test_valid_form_is_accepted():
    data, error = risks.read_form(RISK_FORM)
    assert error is None
    assert (data["likelihood"], data["impact"]) == (3, 4)


@pytest.mark.parametrize("change, message", [
    ({"title": "  "}, "Risikoen må ha en tittel."),
    ({"likelihood": "6"}, "Velg sannsynlighet og konsekvens fra 1 til 5."),
    ({"treatment": "ignorere"}, "Velg en gyldig behandling."),
    ({"review_date": "2026-02-30"}, "Datoen for neste gjennomgang er ugyldig."),
    ({"principle_id": "9.9"}, "Ukjent NSM-prinsipp."),
    ({"residual_likelihood": "2"}, "Velg både sannsynlighet og konsekvens etter tiltak, eller ingen av dem."),
    ({"residual_likelihood": "5", "residual_impact": "5"}, "Restrisikoen kan ikke være høyere enn risikoen før tiltak."),
])
def test_invalid_form_is_refused(change, message):
    _data, error = risks.read_form({**RISK_FORM, **change})
    assert error == message


def make_risk(risk_id, review_date, status="apen"):
    return {"id": risk_id, "title": f"Risiko {risk_id}", "review_date": review_date, "status": status}


def test_reminders_pick_overdue_and_next_30_days_soonest_first():
    rows = [
        make_risk(1, "2026-12-05"),            # in 30 days: included
        make_risk(2, "2026-12-06"),            # in 31 days: too far ahead
        make_risk(3, "2026-11-02"),            # 3 days overdue
        make_risk(4, "2026-11-05"),            # today
        make_risk(5, "2026-10-01", "lukket"),  # closed: never reminded
        make_risk(6, ""),                      # no review date
    ]
    found = risks.reminders(rows, today=TODAY)
    assert [item["id"] for item in found] == [3, 4, 1]
    assert [item["when"] for item in found] == [
        "Forfalt for 3 dager siden", "Gjennomgås i dag", "Gjennomgås om 30 dager"]


@pytest.mark.parametrize("days, text", [
    (-1, "Forfalt for 1 dag siden"), (0, "Gjennomgås i dag"),
    (1, "Gjennomgås i morgen"), (2, "Gjennomgås om 2 dager"),
])
def test_reminder_text(days, text):
    assert risks.reminder_text(days) == text


def test_heat_map_leaves_out_closed_risks():
    items = [risks.enrich({**risks.DEFAULTS, "id": 1, "title": "A", "likelihood": 5, "impact": 5}),
             risks.enrich({**risks.DEFAULTS, "id": 2, "title": "B", "likelihood": 5, "impact": 5,
                           "status": "lukket"})]
    top_right = risks.heat_map(items)[0][4]       # likelihood 5, impact 5
    assert top_right["count"] == 1
