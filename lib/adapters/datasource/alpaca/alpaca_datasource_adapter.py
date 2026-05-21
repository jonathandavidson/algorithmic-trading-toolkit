import time
from collections.abc import Generator

import requests

from lib.adapters.interfaces.datasource_adapter_interface import DatasourceAdapterInterface
from lib.models.alpaca.historical_bar import AlpacaHistoricalBar
from lib.models.base import BaseModel
from lib.services.configuration.collection import CollectionFrequency
from lib.services.configuration.datasource import DatasourceConfiguration
from lib.services.configuration.query import QueryConfiguration
from lib.services.configuration.system import SystemConfigurationService
from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType


class _LazySystemConfig:
    _instance: object | None = None

    def __getattr__(self, name: str) -> object:
        if type(self)._instance is None:
            type(self)._instance = SystemConfigurationService('datasource_adapters').get_one('alpaca')
        return getattr(type(self)._instance, name)


config: _LazySystemConfig = _LazySystemConfig()

_TIMEFRAME_MAP: dict[CollectionFrequency, str] = {
    CollectionFrequency.ONE_DAY: '1D',
    CollectionFrequency.ONE_MINUTE: '1M',
}

_MAX_RETRIES: int = 3
_RETRY_BASE_DELAY: float = 1.0


class AlpacaDatasourceAdapter(DatasourceAdapterInterface):
    def __init__(self, config: DatasourceConfiguration):
        self._config = config

    def convert_to_model(self, data: dict) -> AlpacaHistoricalBar:
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
        return AlpacaHistoricalBar.from_dict(bar_dict)

    def get_model(self, query_config: QueryConfiguration) -> type[BaseModel]:
        if query_config.type == 'historical-bars':
            return AlpacaHistoricalBar
        raise ValueError(f"Unsupported query type: {query_config.type}")

    def _fetch_with_retries(self, params: dict) -> dict:
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
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code < 500:
                    raise
                last_exc = e
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_exc = e

        assert last_exc is not None
        raise last_exc

    def _fetch_historical_bars(self, query_config: HistoricalBarsQueryType) -> Generator[list[AlpacaHistoricalBar], None, None]:
        params: dict = {
            "timeframe": _TIMEFRAME_MAP[CollectionFrequency(query_config.frequency)],
            "start": query_config.start.isoformat(),
            "symbols": ",".join(query_config.symbols),
            "limit": config.page_limit,
        }
        if query_config.end is not None:
            params["end"] = query_config.end.isoformat()

        while True:
            response_data = self._fetch_with_retries(params)
            bars: list[AlpacaHistoricalBar] = []
            for symbol, bars_data in response_data['bars'].items():
                bars.extend([self.convert_to_model({**bar_data, 'symbol': symbol}) for bar_data in bars_data])
            yield bars
            next_page_token: str | None = response_data.get('next_page_token')
            if not next_page_token:
                break
            params = {**params, 'page_token': next_page_token}

    def run_query(self, query_config: QueryConfiguration) -> Generator[list[AlpacaHistoricalBar], None, None]:
        if query_config.type == 'historical-bars':
            fields = {k: v for k, v in query_config.to_dict().items() if k not in ('name', 'type')}
            return self._fetch_historical_bars(HistoricalBarsQueryType(**fields))
        raise ValueError(f"Unsupported query type: {query_config.type}")

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
