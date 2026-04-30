from lib.services.interface.config_service import ConfigServiceInterface
from lib.services.interface.configuration_type import ConfigurationTypeInterface
from lib.utils.config import load_config, save_config


class ConfigurationService(ConfigServiceInterface):

    def __init__(self, type: str, config_class: type[ConfigurationTypeInterface]) -> None:
        self._type = type
        self._config_class = config_class

    def add(self, configuration: ConfigurationTypeInterface) -> ConfigurationTypeInterface:
        config = load_config()
        entries = config.setdefault(self._type, [])
        if any(e["name"] == configuration.name for e in entries):
            raise ValueError(f"'{configuration.name}' already exists.")
        entries.append(configuration.to_dict())
        save_config(config)
        return configuration

    def list(self, name: str) -> list[ConfigurationTypeInterface]:
        return [self._config_class(**e) for e in load_config().get(self._type, [])]

    def remove(self, name: str) -> str:
        config = load_config()
        entries = config.get(self._type, [])
        if not any(e["name"] == name for e in entries):
            raise KeyError(name)
        config[self._type] = [e for e in entries if e["name"] != name]
        save_config(config)
        return name

    def get_one(self, name: str) -> ConfigurationTypeInterface:
        entries = load_config().get(self._type, [])
        entry = next((e for e in entries if e["name"] == name), None)
        if entry is None:
            raise KeyError(name)
        return self._config_class(**entry)
