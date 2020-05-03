import datetime
import json
import re
from typing import List, Dict, Union, Tuple

import bs4
import pytz

from covid_in_russia import models
from covid_in_russia.models import Spread

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


def parse_country_dataset(
    dataset: List[Dict[str, Union[str, int]]],
    retrieved_time: datetime.datetime,
    reported_time: datetime.datetime,
    source_url: str,
) -> List[Spread]:
    """Parse raw dataset about Russia as a whole."""
    return [
        Spread(
            date=datetime.datetime.strptime(row['date'], '%d.%m.%Y').date(),
            reported_time=reported_time,
            retrieved_time=retrieved_time,

            location_iso_code='RU',
            total=row['sick'],
            recovered=row['healed'],
            deceased=row['died'],

            source=source_url,
        )
        for row in dataset
    ]


def parse_regions_dataset(
    dataset: List[Dict[str, Union[str, int]]],
    reported_time: datetime.datetime,
    retrieved_time: datetime.datetime,
    source_url: str,
) -> List[Spread]:
    """Parse raw dataset about Russian regions."""
    return [
        Spread(
            date=reported_time.date(),
            reported_time=reported_time,
            retrieved_time=retrieved_time,

            location_iso_code=row['code'],
            total=row['sick'],
            recovered=row['healed'],
            deceased=row['died'],

            source=source_url,
        )
        for row in dataset
    ]


def parse_html(
    text: str,
    retrieved_time: datetime.datetime,
    source_url: str,
) -> Tuple[List[Spread], List[Spread]]:
    """Parse the website HTML."""
    soup = bs4.BeautifulSoup(text, features='html.parser')

    reported_time = parse_reported_time(
        soup.select_one('.cv-section__title small').text
    )

    raw_country_dataset = json.loads(
        soup.select_one('cv-stats-virus')[':charts-data']
    )

    country_dataset = parse_country_dataset(
        dataset=raw_country_dataset,
        retrieved_time=retrieved_time,
        reported_time=reported_time,
        source_url=source_url
    )

    raw_regions_dataset = json.loads(
        soup.select_one('cv-spread-overview')[':spread-data']
    )

    regions_dataset = parse_regions_dataset(
        dataset=raw_regions_dataset,
        reported_time=reported_time,
        retrieved_time=retrieved_time,
        source_url=source_url,
    )

    return country_dataset, regions_dataset
