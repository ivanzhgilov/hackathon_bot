from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from models.core import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    surname: Mapped[str] = mapped_column(String(256))
    login: Mapped[str] = mapped_column(String(256))
    chat_id: Mapped[int] = mapped_column(
        BigInteger(), index=True, unique=True
    )  # у telegram года так с 22го для id пользователей используется int64
