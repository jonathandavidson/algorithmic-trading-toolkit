from typing import Optional, Self

from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from lib.models.base import BaseModel, CommonMixin


class _HistoricalBarColumns:
    symbol: Mapped[str] = mapped_column(String)
    time: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    open: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    high: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    low: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    close: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    volume: Mapped[Optional[int]] = mapped_column(Numeric(12, 4))
    trade_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    volume_weighted_avg_price: Mapped[Optional[Numeric]] = mapped_column(Numeric(12, 4))

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(**data)


class HistoricalBar(_HistoricalBarColumns, CommonMixin, BaseModel):
    __tablename__ = "historical_bars"


_model_cache: dict[str, type[HistoricalBar]] = {}


def get_historical_bar_model(prefix: str) -> type[HistoricalBar]:
    if prefix in _model_cache:
        return _model_cache[prefix]
    model: type[HistoricalBar] = type(
        f"HistoricalBar_{prefix}",
        (_HistoricalBarColumns, CommonMixin, BaseModel),
        {"__tablename__": f"{prefix}_historical_bars"},
    )
    _model_cache[prefix] = model
    return model
