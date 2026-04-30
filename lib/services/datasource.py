import requests

from lib.services.configuration import ConfigurationService

_config = ConfigurationService("datasources")
_TEST_URLS = {
    "alpaca": "https://data.alpaca.markets/v1beta3/crypto/us/bars",
}


def add(name: str, datasource_type: str, api_key: str, api_secret: str) -> dict:
    entry = {
        "name": name,
        "type": datasource_type,
        "api_key": api_key,
        "api_secret": api_secret,
    }
    return _config.add(name, entry)


def list() -> list[dict]:
    return _config.list("name")


def remove(name: str) -> str:
    return _config.remove(name)


def test(name: str) -> str:
    datasources = _config.list("name")
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
