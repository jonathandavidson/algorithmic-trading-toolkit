from lib.models.historical_bars import HistoricalBar, get_historical_bar_model


def test_default_table_name() -> None:
    assert HistoricalBar.__tablename__ == "historical_bars"


def test_factory_sets_table_name() -> None:
    model = get_historical_bar_model("myprefix")
    assert model.__tablename__ == "myprefix_historical_bars"


def test_factory_returns_same_class_for_same_prefix() -> None:
    a = get_historical_bar_model("alpha")
    b = get_historical_bar_model("alpha")
    assert a is b


def test_factory_returns_different_classes_for_different_prefixes() -> None:
    a = get_historical_bar_model("foo")
    b = get_historical_bar_model("bar")
    assert a is not b
    assert a.__tablename__ == "foo_historical_bars"
    assert b.__tablename__ == "bar_historical_bars"


def test_factory_model_has_all_columns() -> None:
    model = get_historical_bar_model("coltest")
    column_names = {c.key for c in model.__table__.columns}
    expected = {"id", "created_at", "updated_at", "source", "symbol", "time",
                "open", "high", "low", "close", "volume", "trade_count",
                "volume_weighted_avg_price"}
    assert expected == column_names
