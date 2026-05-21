from typing import Optional, Self

from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from lib.models.base import BaseModel, CommonMixin


class HistoricalBars(CommonMixin, BaseModel):
    __abstract__ = True

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
