import dataclasses
import operator

import bs4

from covid_in_russia import models


def _fetch_cell(row: bs4.Tag, selector: str) -> int:
    """Fetch individual cell value."""
    return int(row.select_one(selector).parent.text)


def _row_to_record(row: bs4.Tag) -> models.Record:
    """Convert a tr tag into Record model."""
    return models.Record(
        region=row.th.text.strip(),
        total=_fetch_cell(row, '.d-map__indicator_sick'),
        recovered=_fetch_cell(row, '.d-map__indicator_healed'),
        deceased=_fetch_cell(row, '.d-map__indicator_die'),
    )


def parse_html(text: str) -> models.Report:
    """Parse the website HTML."""
    soup = bs4.BeautifulSoup(text, features='html.parser')

    rows = soup.select('#map_popup .d-map__list table tr')

    return models.Report(
        per_region=list(map(_row_to_record, rows)),
    )


def calculate_totals(report: models.Report) -> models.Report:
    """Calculate total values."""
    total_cases = sum(map(operator.attrgetter('total'), report.per_region))

    recovered_cases = sum(map(
        operator.attrgetter('recovered'),
        report.per_region,
    ))

    deceased_cases = sum(map(
        operator.attrgetter('deceased'), report.per_region,
    ))

    return dataclasses.replace(
        report,
        totals=models.Totals(
            total=total_cases,
            recovered=recovered_cases,
            deceased=deceased_cases,
        )
    )
