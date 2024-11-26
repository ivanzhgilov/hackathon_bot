from schemas.core import Model, IdMixin


class UserInit(Model):
    chat_id: int
    login: str
    name: str | None


# class User(Base, TimestampMixin):
#     __tablename__ = 'users'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str | None] = mapped_column(String(256))
#     login: Mapped[str | None] = mapped_column(String(256))
#     hashed_password: Mapped[str | None] = mapped_column(String(256))
#     login_status: Mapped[bool] = mapped_column(default=False)
#     chat_id: Mapped[int] = mapped_column(
#         BigInteger(), index=True, unique=True
#     )

class UserAccount(Model):
    hashed_password: str | None
    login_status: bool | None


class UserShort(UserInit, IdMixin):
    hashed_password: str | None
    login_status: bool | None
