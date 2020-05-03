import dataclasses
import datetime
import time
from datetime import date
from typing import Optional, Dict, NewType, List


def timestamp():
    return int(time.time() * 1000)


@dataclasses.dataclass(frozen=True)
class Record:
    region: str
    total: int = 0
    recovered: int = 0
    deceased: int = 0


@dataclasses.dataclass(frozen=True)
class Totals:
    total: int = 0
    recovered: int = 0
    deceased: int = 0


@dataclasses.dataclass(frozen=True)
class Report:
    per_region: List[Record]
    reported_time: Optional[datetime.datetime] = None

    totals: Optional[Totals] = None

    parsed_time: Optional[int] = None

    index_cid: Optional[str] = None
    page_cid: Optional[str] = None

    calculated_time: Optional[int] = dataclasses.field(default_factory=timestamp)


@dataclasses.dataclass(frozen=True)
class Spread:
    date: datetime.date
    reported_time: datetime.datetime
    retrieved_time: datetime.datetime

    location_iso_code: str

    total: int
    recovered: int
    deceased: int

    source: str
