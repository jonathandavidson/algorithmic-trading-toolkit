import time

import requests

from lib.adapters.interfaces.datasource_adapter_interface import DatasourceAdapterInterface
from lib.services.configuration.collection import CollectionConfiguration, CollectionFrequency
from lib.services.configuration.datasource import DatasourceConfiguration
from lib.models.historical_bars import HistoricalBar
from lib.services.configuration.system import SystemConfigurationService

config = SystemConfigurationService('datasource_adapters').get_one('alpaca')

_TIMEFRAME_MAP: dict[CollectionFrequency, str] = {
    CollectionFrequency.ONE_DAY: '1D',
    CollectionFrequency.ONE_MINUTE: '1M',
}

_MAX_RETRIES: int = 3
_RETRY_BASE_DELAY: float = 1.0


class AlpacaDatasourceAdapter(DatasourceAdapterInterface):
    def __init__(self, config: DatasourceConfiguration):
        self._config = config

    def convert_to_model(self, data: dict) -> HistoricalBar:
        bar_dict = {
            'symbol': data['symbol'],
            'time': data['t'],
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'close': data['c'],
            'volume': data['v'],
            'trade_count': data['n'],
            'volume_weighted_avg_price': data['vw'],
            'source': self._config.type
        }
        return HistoricalBar.from_dict(bar_dict)
    
    def fetch_rows(self, collection_config: CollectionConfiguration) -> list[HistoricalBar]:
        params: dict = {
            "timeframe": _TIMEFRAME_MAP[collection_config.frequency],
            "start": collection_config.start.isoformat(),
            "limit": 1000,
        }
        if collection_config.symbols is not None:
            params["symbols"] = ",".join(collection_config.symbols)
        if collection_config.end is not None:
            params["end"] = collection_config.end.isoformat()

        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            if attempt > 0:
                time.sleep(_RETRY_BASE_DELAY * (2 ** (attempt - 1)))
            try:
                response = requests.get(
                    config.fetch_url,
                    auth=(self._config.api_key, self._config.api_secret),
                    headers={"accept": "application/json"},
                    params=params,
                )
                response.raise_for_status()
                response_data = response.json()
                bars = []
                for symbol, bars_data in response_data['bars'].items():
                    bars.extend([self.convert_to_model({**bar_data, 'symbol': symbol}) for bar_data in bars_data])
                return bars
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code < 500:
                    raise
                last_exc = e
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_exc = e

        assert last_exc is not None
        raise last_exc
    
    def test_connection(self) -> bool:
        url = config.test_url
        print(f"Testing connection to {url} with API key {self._config.api_key}")
        response = requests.get(
            url,
            auth=(self._config.api_key, self._config.api_secret),
            headers={"accept": "application/json"},
            params={"symbols": "BTC/USD", "timeframe": "1D"},
        )
        response.raise_for_status()
        return True
