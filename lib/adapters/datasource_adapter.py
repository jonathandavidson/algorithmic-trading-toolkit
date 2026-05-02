import requests
import json

from lib.services.configuration.datasource import DatasourceConfiguration
from lib.models.historical_bars import HistoricalBar


_TEST_URLS = {
    'alpaca': 'https://data.alpaca.markets/v1beta3/crypto/us/bars',
}

_MOCK_RESPONSE_DATA = '''
    {
        "bars": {
            "BTC/USD": [
                {
                    "t": "2026-05-27T10:18:00Z",
                    "o": 28999,
                    "h": 29003,
                    "l": 28999,
                    "c": 29003,
                    "v": 0.01,
                    "n": 4,
                    "vw": 29001
                },
                {
                    "t": "2022-05-27T10:18:00Z",
                    "o": 28999,
                    "h": 29003,
                    "l": 28999,
                    "c": 29003,
                    "v": 0.01,
                    "n": 4,
                    "vw": 29001
                }
            ]
        },
        "next_page_token": "MTY0MDk0ODkyMzAwMDAwMDAwMHwyNDg0MzE3MQ=="
    }
'''

class DatasourceAdapter:

    def __init__(self, config: DatasourceConfiguration):
        self._config = config

    def _convert_to_model(self, data: dict) -> HistoricalBar:
        bar_dict = {
            'symbol': data['symbol'],
            'time': data['t'],
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'close': data['c'],
            'volume': data['v'],
        }
        return HistoricalBar.from_dict(bar_dict)

    def fetch_historical_bars(self) -> list[HistoricalBar]:
        response_data = json.loads(_MOCK_RESPONSE_DATA)
        bars = []
        for symbol, bars_data in response_data['bars'].items():
            bars.extend([self._convert_to_model({**bar_data, 'symbol': symbol}) for bar_data in bars_data])
        return bars

    def test_connection(self) -> bool:
        url = _TEST_URLS[self._config.type]
        response = requests.get(
            url,
            auth=(self._config.api_key, self._config.api_secret),
            headers={"accept": "application/json"},
            params={"symbols": "BTC/USD", "timeframe": "1D"},
        )
        response.raise_for_status()
        return True
