from sqlalchemy.orm import Session

from lib.utils.database import get_engine
from lib.services.configuration.database import DatabaseConfiguration
from lib.models.base import Base
from lib.models.historical_bars import HistoricalBar


class DatabaseInsertError(Exception):
    pass


class DatabaseAdapter:

    _config: DatabaseConfiguration

    def __init__(self, config: DatabaseConfiguration):
        self._config = config

    def _get_engine(self):
        return get_engine(self._config.to_dict())
    
    def init_database(self):
        engine = self._get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def test_connection(self) -> bool:
        engine = self._get_engine()
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True

    def insert_historical_bars(self, bars: list[HistoricalBar]):
        engine = self._get_engine()
        with Session(engine) as session:
            session.add_all(bars)
            session.commit()
