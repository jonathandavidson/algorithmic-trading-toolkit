import dataclasses
from dataclasses import dataclass

from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.interface.config_service import ConfigServiceInterface
from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface
from lib.utils.crypto import decrypt_secret, encrypt_secret
from lib.utils.database import connect


@dataclass
class DatabaseConfiguration(ConfigurationTypeInterface):
    name: str
    type: str
    username: str
    password: str
    host: str
    port: int
    dbname: str

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d


class DatabaseConfigurationService(ConfigServiceInterface):

    def __init__(self) -> None:
        self._config = ConfigurationService("databases", DatabaseConfiguration)

    def add(self, configuration: DatabaseConfiguration) -> DatabaseConfiguration:  # type: ignore[override]
        encrypted = DatabaseConfiguration(
            name=configuration.name,
            type=configuration.type,
            username=configuration.username,
            password=encrypt_secret(configuration.password),
            host=configuration.host,
            port=configuration.port,
            dbname=configuration.dbname,
        )
        self._config.add(encrypted)
        return configuration

    def list(self, name: str = "name") -> list[DatabaseConfiguration]:  # type: ignore[override]
        return self._config.list(name)  # type: ignore[return-value]

    def get_one(self, name: str) -> DatabaseConfiguration:  # type: ignore[override]
        entry = self._config.get_one(name)  # type: ignore[assignment]
        return DatabaseConfiguration(
            name=entry.name,
            type=entry.type,
            username=entry.username,
            password=decrypt_secret(entry.password),
            host=entry.host,
            port=entry.port,
            dbname=entry.dbname,
        )

    def remove(self, name: str) -> str:
        return self._config.remove(name)

    def test(self, name: str) -> str:
        db = self.get_one(name)
        with connect(db.to_dict()):
            pass
        return name
