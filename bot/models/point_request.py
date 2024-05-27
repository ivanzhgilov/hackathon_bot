from sqlalchemy import String, BigInteger, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.core import Base, TimestampMixin


class PointRequest(Base, TimestampMixin):
    __tablename__ = 'point_request'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(256))
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(String(1024))
    address: Mapped[str] = mapped_column(String(256))
    phone_number: Mapped[str | None] = mapped_column(String(20))
    types_of_garbage: Mapped[str] = mapped_column(String(256))
    lat: Mapped[float | None] = mapped_column(Float())
    lon: Mapped[float | None] = mapped_column(Float())