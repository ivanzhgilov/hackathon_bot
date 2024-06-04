from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.core import Base, TimestampMixin


class Command(Base, TimestampMixin):
    __tablename__ = 'commands'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    user: Mapped[str] = mapped_column(String(256))
