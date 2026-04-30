from lib.utils.config import load_config, save_config


def add(type: str, name: str, configuration: dict) -> dict:
    config = load_config()
    entries = config.setdefault(type, [])
    if any(e["name"] == name for e in entries):
        raise ValueError(f"'{name}' already exists.")
    entries.append(configuration)
    save_config(config)
    return configuration


def list(type: str, name: str) -> list[dict]:
    return load_config().get(type, [])


def remove(type: str, name: str) -> str:
    config = load_config()
    entries = config.get(type, [])
    if not any(e["name"] == name for e in entries):
        raise KeyError(name)
    config[type] = [e for e in entries if e["name"] != name]
    save_config(config)
    return name
