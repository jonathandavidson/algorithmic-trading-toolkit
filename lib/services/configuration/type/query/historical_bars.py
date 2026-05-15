from dataclasses import dataclass
from datetime import datetime, timezone
from typing import ClassVar

from lib.services.configuration.collection import CollectionFrequency


@dataclass
class HistoricalBarsQueryType:
    name: ClassVar[str] = 'historical-bars'
    symbols: list[str]
    frequency: str
    start: datetime | None = None
    end: datetime | None = None

    def __post_init__(self) -> None:
        CollectionFrequency(self.frequency)
        if self.start is not None:
            self.start = self._parse_dt(self.start)
        if self.end is not None:
            self.end = self._parse_dt(self.end)

    @staticmethod
    def _parse_dt(value: datetime | str) -> datetime:
        dt = datetime.fromisoformat(value) if isinstance(value, str) else value
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def to_dict(self) -> dict:
        d: dict = {
            'symbols': self.symbols,
            'frequency': self.frequency,
        }
        if self.start is not None:
            d['start'] = self.start.isoformat()
        if self.end is not None:
            d['end'] = self.end.isoformat()
        return d
