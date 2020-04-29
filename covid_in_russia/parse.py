import dataclasses
import datetime
import operator
import re

import bs4
import pytz

from covid_in_russia import models

MONTHS = (
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря',
)


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


def parse_reported_time(raw_time: str) -> datetime.datetime:
    groups = re.match(
        (
            r'По состоянию на (?P<day>\d+) (?P<month>\w+) ' +
            r'(?P<hour>\d+):(?P<minute>\d+)'
        ),
        raw_time
    ).groupdict()

    return datetime.datetime(
        year=2020,
        month=MONTHS.index(groups['month']) + 1,
        day=int(groups['day']),
        hour=int(groups['hour']),
        minute=int(groups['minute']),
    ).astimezone(
        pytz.timezone('Europe/Moscow'),
    )


def parse_html(text: str) -> models.Report:
    """Parse the website HTML."""
    soup = bs4.BeautifulSoup(text, features='html.parser')

    raw_time = soup.select_one('.cv-banner__description').text

    rows = soup.select('#map_popup .d-map__list table tr')

    return models.Report(
        reported_time=parse_reported_time(raw_time),
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
