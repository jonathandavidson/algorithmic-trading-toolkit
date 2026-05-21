from lib.models.alpaca.historical_bar import AlpacaHistoricalBar
from lib.models.historical_bars import HistoricalBars


def test_historical_bars_is_abstract() -> None:
    assert HistoricalBars.__abstract__ is True


def test_alpaca_historical_bar_tablename() -> None:
    assert AlpacaHistoricalBar.__tablename__ == "alpaca_historical_bars"


def test_alpaca_historical_bar_has_all_columns() -> None:
    column_names = {c.key for c in AlpacaHistoricalBar.__table__.columns}
    expected = {
        "id", "created_at", "updated_at", "source",
        "symbol", "time", "open", "high", "low", "close",
        "volume", "trade_count", "volume_weighted_avg_price",
    }
    assert expected == column_names


def test_alpaca_historical_bar_from_dict() -> None:
    data = {
        "symbol": "BTC/USD",
        "time": "2026-01-01T00:00:00Z",
        "open": 100,
        "high": 200,
        "low": 50,
        "close": 150,
        "volume": 1.5,
        "trade_count": 4,
        "volume_weighted_avg_price": 125,
    }
    bar = AlpacaHistoricalBar.from_dict(data)
    assert bar.symbol == "BTC/USD"
    assert bar.open == 100
