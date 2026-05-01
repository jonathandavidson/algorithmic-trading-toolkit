import dataclasses
from abc import ABC


class ConfigurationTypeInterface(ABC):
    name: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
