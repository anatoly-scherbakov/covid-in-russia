from pathlib import Path

import pytest

from covid_in_russia import parse, models


@pytest.fixture()
def html() -> str:
    with open(Path(__file__).parent / 'data/index.html', 'r') as f:
        return f.read()


def test_parse(html: str):
    report = parse.parse_html(html)

    moscow: models.Record
    moscow, *etc = report.per_region

    assert moscow == models.Record(
        region='Москва',
        total=18105,
        recovered=1517,
        deceased=127,
    )


def test_calculate_totals(html: str):
    report = parse.parse_html(html)
    report = parse.calculate_totals(report)

    assert report.totals == models.Totals(
        total=32008,
        recovered=2590,
        deceased=273,
    )
