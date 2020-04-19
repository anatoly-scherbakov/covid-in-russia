import dataclasses
import time
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
    totals: Optional[Totals] = None
    timestamp: Optional[int] = dataclasses.field(default_factory=timestamp)
