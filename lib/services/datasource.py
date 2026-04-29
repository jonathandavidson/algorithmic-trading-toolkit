from lib.config import load_config, save_config


def add(name: str, datasource_type: str, api_key: str, api_secret: str) -> dict:
    config = load_config()
    datasources = config.setdefault("datasources", [])
    if any(ds["name"] == name for ds in datasources):
        raise ValueError(f"Datasource '{name}' already exists.")
    entry = {
        "name": name,
        "type": datasource_type,
        "api_key": api_key,
        "api_secret": api_secret,
    }
    datasources.append(entry)
    save_config(config)
    return entry
