import sqlalchemy
import sqlalchemy.orm


class CommonMixin:
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        sqlalchemy.BigInteger, primary_key=True
    )
    created_time: sqlalchemy.orm.Mapped[sqlalchemy.DateTime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True)
    )
    updated_time: sqlalchemy.orm.Mapped[sqlalchemy.DateTime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True)
    )


class Base(sqlalchemy.orm.DeclarativeBase):
    pass
