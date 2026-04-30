from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from lib.utils.config import load_config, save_config
from lib.utils.database import get_engine
from lib.models.base import Base
from lib.models.historical_bars import HistoricalBar
import lib.models.historical_bars  # registers HistoricalBar with Base.metadata


class CollectionNotFoundError(LookupError):
    pass


class DatabaseNotFoundError(LookupError):
    pass


def _find_collection(name: str) -> dict:
    config = load_config()
    collection = next((c for c in config.get("collections", []) if c["name"] == name), None)
    if collection is None:
        raise CollectionNotFoundError(name)
    return collection


def _find_database(collection: dict) -> dict:
    config = load_config()
    db = next((d for d in config.get("databases", []) if d["name"] == collection["database"]), None)
    if db is None:
        raise DatabaseNotFoundError(collection["database"])
    return db


def add(name: str, database: str, type: str, start: str, frequency: str | None = None, end: str | None = None) -> dict:
    config = load_config()
    collections = config.setdefault("collections", [])
    if any(c["name"] == name for c in collections):
        raise ValueError(f"Collection '{name}' already exists.")
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
    collections.append(entry)
    save_config(config)
    return entry


def list() -> list[dict]:
    return load_config().get("collections", [])


def remove(name: str) -> str:
    config = load_config()
    collections = config.get("collections", [])
    if not any(c["name"] == name for c in collections):
        raise CollectionNotFoundError(name)
    config["collections"] = [c for c in collections if c["name"] != name]
    save_config(config)
    return name


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
