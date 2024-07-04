import datetime

from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, declarative_mixin, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


@declarative_mixin
class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now()
    )


@declarative_mixin
class SoftDeleteMixin:
    """
    Фильтрация удалённых объектов на совести использующего этот миксин
    """
    deleted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
