from lib.services.interface.config_service import ConfigServiceInterface
from lib.utils.config import load_config, save_config


class ConfigurationService(ConfigServiceInterface):

    def __init__(self, type: str) -> None:
        self._type = type

    def add(self, name: str, configuration: dict) -> dict:
        config = load_config()
        entries = config.setdefault(self._type, [])
        if any(e["name"] == name for e in entries):
            raise ValueError(f"'{name}' already exists.")
        entries.append(configuration)
        save_config(config)
        return configuration

    def list(self, name: str) -> list[dict]:
        return load_config().get(self._type, [])

    def get_one(self, name: str) -> dict:
        entries = load_config().get(self._type, [])
        entry = next((e for e in entries if e["name"] == name), None)
        if entry is None:
            raise KeyError(name)
        return entry

    def remove(self, name: str) -> str:
        config = load_config()
        entries = config.get(self._type, [])
        if not any(e["name"] == name for e in entries):
            raise KeyError(name)
        config[self._type] = [e for e in entries if e["name"] != name]
        save_config(config)
        return name
