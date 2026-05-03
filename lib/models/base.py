from typing import Optional

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CommonMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), insert_default=func.now())
    source: Mapped[Optional[str]] = mapped_column(String)


class BaseModel(DeclarativeBase):
    pass
