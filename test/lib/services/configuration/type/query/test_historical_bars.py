import pytest
from datetime import datetime, timezone

from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType


def test_name_is_class_constant():
    assert HistoricalBarsQueryType.name == 'historical-bars'


def test_valid_construction():
    qt = HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='1d')
    assert qt.symbols == ['BTC/USD']
    assert qt.frequency == '1d'
    assert qt.start is None
    assert qt.end is None


def test_symbols_required():
    with pytest.raises(TypeError):
        HistoricalBarsQueryType(frequency='1d')  # type: ignore[call-arg]


def test_frequency_required():
    with pytest.raises(TypeError):
        HistoricalBarsQueryType(symbols=['BTC/USD'])  # type: ignore[call-arg]


def test_invalid_frequency_raises():
    with pytest.raises(ValueError):
        HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='5m')


def test_valid_frequencies():
    HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='1d')
    HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='1m')


def test_start_parsed_from_string():
    qt = HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='1d', start='2024-01-01T00:00:00')
    assert isinstance(qt.start, datetime)
    assert qt.start.tzinfo == timezone.utc


def test_end_parsed_from_string():
    qt = HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='1d', end='2024-06-01T00:00:00')
    assert isinstance(qt.end, datetime)
    assert qt.end.tzinfo == timezone.utc


def test_datetime_with_tz_preserved():
    qt = HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='1d', start='2024-01-01T00:00:00+05:00')
    assert qt.start is not None
    assert qt.start.utcoffset() is not None


def test_to_dict_required_fields():
    qt = HistoricalBarsQueryType(symbols=['BTC/USD', 'ETH/USD'], frequency='1d')
    d = qt.to_dict()
    assert d['symbols'] == ['BTC/USD', 'ETH/USD']
    assert d['frequency'] == '1d'
    assert 'start' not in d
    assert 'end' not in d


def test_to_dict_with_optional_fields():
    qt = HistoricalBarsQueryType(
        symbols=['BTC/USD'],
        frequency='1m',
        start='2024-01-01T00:00:00',
        end='2024-06-01T00:00:00',
    )
    d = qt.to_dict()
    assert 'start' in d
    assert 'end' in d
    assert isinstance(d['start'], str)
    assert isinstance(d['end'], str)


def test_to_dict_excludes_name():
    qt = HistoricalBarsQueryType(symbols=['BTC/USD'], frequency='1d')
    assert 'name' not in qt.to_dict()
