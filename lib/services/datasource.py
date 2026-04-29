import requests

from lib.config import load_config, save_config

_TEST_URLS = {
    "alpaca": "https://data.alpaca.markets/v1beta3/crypto/us/bars",
}


def list() -> list[dict]:
    return load_config().get("datasources", [])


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


def test(name: str) -> str:
    datasources = load_config().get("datasources", [])
    ds = next((d for d in datasources if d["name"] == name), None)
    if ds is None:
        raise KeyError(name)
    url = _TEST_URLS[ds["type"]]
    response = requests.get(
        url,
        auth=(ds["api_key"], ds["api_secret"]),
        headers={"accept": "application/json"},
        params={"symbols": "BTC/USD", "timeframe": "1D"},
    )
    response.raise_for_status()
    return name


def remove(name: str) -> str:
    config = load_config()
    datasources = config.get("datasources", [])
    if not any(ds["name"] == name for ds in datasources):
        raise KeyError(name)
    config["datasources"] = [ds for ds in datasources if ds["name"] != name]
    save_config(config)
    return name
