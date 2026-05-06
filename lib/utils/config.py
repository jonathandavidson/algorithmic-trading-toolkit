import os

import yaml

_CONFIG_PATH_TEMPLATE = ".config/{config_type}.config.yaml"


def load_config(config_type: str = "user") -> dict:
    path = _CONFIG_PATH_TEMPLATE.format(config_type=config_type)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict, config_type: str = "user") -> None:
    path = _CONFIG_PATH_TEMPLATE.format(config_type=config_type)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
