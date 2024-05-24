from sqlalchemy import String, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.core import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(256))
    surname: Mapped[str | None] = mapped_column(String(256))
    login: Mapped[str | None] = mapped_column(String(256))
    chat_id: Mapped[int] = mapped_column(
        BigInteger(), index=True, unique=True
    )  # у telegram года так с 22го для id пользователей используется int64
    about: Mapped[dict | None] = mapped_column(JSONB())
    admin: Mapped[bool] = mapped_column(default=False)
