from typing import Optional

from sqlalchemy import BigInteger, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from lib.models.base import Base, CommonMixin


class HistoricalBar(CommonMixin, Base):
    __tablename__ = "historical_bars"

    time: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    open: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    high: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    low: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    close: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    volume: Mapped[Optional[int]] = mapped_column(BigInteger)
    trade_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    volume_weighted_avg_price: Mapped[Optional[Numeric]] = mapped_column(Numeric(12, 4))
