from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType

_REGISTRY: dict[str, type] = {
    HistoricalBarsQueryType.name: HistoricalBarsQueryType,
}


def get_query_type_class(name: str) -> type:
    if name not in _REGISTRY:
        raise KeyError(f"Unknown query type: {name!r}")
    return _REGISTRY[name]
