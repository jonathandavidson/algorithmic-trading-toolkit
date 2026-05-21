from sqlalchemy.orm import Session

from lib.utils.database import get_engine
from lib.services.configuration.database import DatabaseConfiguration
from lib.models.base import BaseModel


class DatabaseInsertError(Exception):
    pass


class DatabaseAdapter:

    _config: DatabaseConfiguration

    def __init__(self, config: DatabaseConfiguration):
        self._config = config

    @staticmethod
    def get_instance(config: DatabaseConfiguration) -> 'DatabaseAdapter':
        return DatabaseAdapter(config)

    def _get_engine(self):
        return get_engine(self._config.to_dict())
    
    def init_database(self):
        engine = self._get_engine()
        BaseModel.metadata.drop_all(engine)
        BaseModel.metadata.create_all(engine)

    def init_model(self, model: type[BaseModel]) -> None:
        engine = self._get_engine()
        model.__table__.drop(engine, checkfirst=True)
        model.__table__.create(engine, checkfirst=True)

    def test_connection(self) -> bool:
        engine = self._get_engine()
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True

    def insert_rows(self, bars: list[BaseModel]):
        engine = self._get_engine()
        with Session(engine) as session:
            session.add_all(bars)
            session.commit()
