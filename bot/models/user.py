from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from models.core import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(256), default=None)
    login: Mapped[str | None] = mapped_column(String(256), unique=True)
    hashed_password: Mapped[str | None] = mapped_column(String(256), default=None)
    login_status: Mapped[bool] = mapped_column(default=False)
    chat_id: Mapped[int] = mapped_column(
        BigInteger(), index=True, unique=True
    )