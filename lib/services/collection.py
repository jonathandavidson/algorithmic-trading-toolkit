from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from lib.services.configuration import ConfigurationService
from lib.utils.database import get_engine
from lib.models.base import Base
from lib.models.historical_bars import HistoricalBar
import lib.models.historical_bars  # registers HistoricalBar with Base.metadata

_config = ConfigurationService("collections")
_db_config = ConfigurationService("databases")


class CollectionNotFoundError(LookupError):
    pass


class DatabaseNotFoundError(LookupError):
    pass


def _find_collection(name: str) -> dict:
    try:
        return _config.get_one(name)
    except KeyError:
        raise CollectionNotFoundError(name)


def _find_database(collection: dict) -> dict:
    try:
        return _db_config.get_one(collection["database"])
    except KeyError:
        raise DatabaseNotFoundError(collection["database"])


def add(name: str, database: str, type: str, start: str, frequency: str | None = None, end: str | None = None) -> dict:
    entry = {
        "name": name,
        "database": database,
        "type": type,
        "start": start,
    }
    if frequency is not None:
        entry["frequency"] = frequency
    if end is not None:
        entry["end"] = end
    return _config.add(name, entry)


def list() -> list[dict]:
    return _config.list("name")


def remove(name: str) -> str:
    try:
        return _config.remove(name)
    except KeyError:
        raise CollectionNotFoundError(name)


def init(name: str) -> str:
    collection = _find_collection(name)
    db = _find_database(collection)
    engine = get_engine(db)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return name


def run(name: str) -> int:
    collection = _find_collection(name)
    db = _find_database(collection)
    engine = get_engine(db)
    now = datetime.now(timezone.utc)

    bars = [
        HistoricalBar(
            id=1,
            collection_name=collection["name"],
            symbol="AAPL",
            time=datetime(2024, 1, 2, 9, 30, tzinfo=timezone.utc),
            open=Decimal("185.0000"),
            high=Decimal("186.5000"),
            low=Decimal("184.2500"),
            close=Decimal("186.1900"),
            volume=45231000,
            trade_count=312400,
            volume_weighted_avg_price=Decimal("185.7500"),
            created_at=now,
            updated_at=now,
        ),
        HistoricalBar(
            id=2,
            collection_name=collection["name"],
            symbol="AAPL",
            time=datetime(2024, 1, 3, 9, 30, tzinfo=timezone.utc),
            open=Decimal("184.2200"),
            high=Decimal("185.8800"),
            low=Decimal("183.4300"),
            close=Decimal("184.9200"),
            volume=53412000,
            trade_count=345600,
            volume_weighted_avg_price=Decimal("184.8100"),
            created_at=now,
            updated_at=now,
        ),
        HistoricalBar(
            id=3,
            collection_name=collection["name"],
            symbol="AAPL",
            time=datetime(2024, 1, 4, 9, 30, tzinfo=timezone.utc),
            open=Decimal("182.1500"),
            high=Decimal("183.9000"),
            low=Decimal("181.5000"),
            close=Decimal("181.9100"),
            volume=47865000,
            trade_count=298700,
            volume_weighted_avg_price=Decimal("182.7300"),
            created_at=now,
            updated_at=now,
        ),
    ]

    with Session(engine) as session:
        session.add_all(bars)
        session.commit()

    return len(bars)
