import sqlalchemy
import sqlalchemy.orm

from lib.models.base import Base, CommonMixin


class HistoricalBar(CommonMixin, Base):
    __tablename__ = "historical_bars"

    time: sqlalchemy.orm.Mapped[sqlalchemy.DateTime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True)
    )
    open: sqlalchemy.orm.Mapped[sqlalchemy.Numeric] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Numeric
    )
    high: sqlalchemy.orm.Mapped[sqlalchemy.Numeric] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Numeric
    )
    low: sqlalchemy.orm.Mapped[sqlalchemy.Numeric] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Numeric
    )
    close: sqlalchemy.orm.Mapped[sqlalchemy.Numeric] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Numeric
    )
    volume: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(sqlalchemy.BigInteger)
    trade_count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(sqlalchemy.BigInteger)
    volume_weighted_avg_price: sqlalchemy.orm.Mapped[sqlalchemy.Numeric] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Numeric
    )
