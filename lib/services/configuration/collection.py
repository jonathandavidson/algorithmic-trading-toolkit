import dataclasses
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.database import DatabaseConfiguration
from lib.services.configuration.interface.config_service import ConfigServiceInterface
from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface
from lib.utils.database import get_engine
from lib.models.base import Base
from lib.models.historical_bars import HistoricalBar
import lib.models.historical_bars  # registers HistoricalBar with Base.metadata


class CollectionNotFoundError(LookupError):
    pass


class DatabaseNotFoundError(LookupError):
    pass

class DatasourceNotFoundError(LookupError):
    pass


@dataclass
class CollectionConfiguration(ConfigurationTypeInterface):
    name: str
    database: str
    type: str
    start: str
    datasource: str | None = None
    frequency: str | None = None
    end: str | None = None

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        if d["frequency"] is None:
            del d["frequency"]
        if d["end"] is None:
            del d["end"]
        return d


class CollectionConfigurationService(ConfigServiceInterface):

    def __init__(self) -> None:
        self._config = ConfigurationService("collections", CollectionConfiguration)
        self._db_config = ConfigurationService("databases", DatabaseConfiguration)

    def _find_collection(self, name: str) -> CollectionConfiguration:
        try:
            return self._config.get_one(name)  # type: ignore[return-value]
        except KeyError:
            raise CollectionNotFoundError(name)

    def _find_database(self, collection: CollectionConfiguration) -> DatabaseConfiguration:
        try:
            return self._db_config.get_one(collection.database)  # type: ignore[return-value]
        except KeyError:
            raise DatabaseNotFoundError(collection.database)

    def add(self, configuration: CollectionConfiguration) -> CollectionConfiguration:  # type: ignore[override]
        return self._config.add(configuration)  # type: ignore[return-value]

    def list(self, name: str = "name") -> list[CollectionConfiguration]:  # type: ignore[override]
        return self._config.list(name)  # type: ignore[return-value]

    def get_one(self, name: str) -> CollectionConfiguration:  # type: ignore[override]
        return self._config.get_one(name)  # type: ignore[return-value]

    def remove(self, name: str) -> str:
        try:
            return self._config.remove(name)
        except KeyError:
            raise CollectionNotFoundError(name)

    def init(self, name: str) -> str:
        collection = self._find_collection(name)
        db = self._find_database(collection)
        engine = get_engine(db.to_dict())
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        return name

    def run(self, name: str) -> int:
        collection = self._find_collection(name)
        db = self._find_database(collection)
        engine = get_engine(db.to_dict())
        now = datetime.now(timezone.utc)

        bars = [
            HistoricalBar(
                id=1,
                collection_name=collection.name,
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
                collection_name=collection.name,
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
                collection_name=collection.name,
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
