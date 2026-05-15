import pytest

from lib.services.configuration.type.query.factory import get_query_type_class
from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType


def test_known_type_returns_class():
    cls = get_query_type_class('historical-bars')
    assert cls is HistoricalBarsQueryType


def test_unknown_type_raises():
    with pytest.raises(KeyError):
        get_query_type_class('unknown-type')
