import dataclasses
import json
from typing import List, Optional, Dict


@dataclasses.dataclass(frozen=True)
class WebArchiveRecord:
    location: str
    timestamp: int
    data: Dict[str, str]


def record_from_line(line: str) -> Optional[WebArchiveRecord]:
    """Parse a WebArchiveRecord from a CDXJ line."""

    if line.startswith('!'):
        return None

    if not line:
        return None

    location, timestamp, json_data = line.split(' ', 2)

    return WebArchiveRecord(
        location=location,
        timestamp=int(timestamp),
        data=json.loads(json_data),
    )


class WebArchiveIndex(List[WebArchiveRecord]):
    @classmethod
    def from_string(cls, value: str) -> 'WebArchiveIndex':
        lines = value.split('\n')
        maybe_records = map(record_from_line, lines)
        records = filter(bool, maybe_records)   # type: ignore
        return WebArchiveIndex(list(records))

    def find_by_original_uri(self, uri: str) -> Optional[WebArchiveRecord]:
        for record in self:
            if record.data.get('original_uri') == uri:
                return record
