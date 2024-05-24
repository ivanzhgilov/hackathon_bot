from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.core import Base


class AdminPassword(Base):
    __tablename__ = 'admin_password'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    password: Mapped[str] = mapped_column(String(256))
