from schemas.core import Model, IdMixin


class UserInit(Model):
    chat_id: int
    login: str
    name: str | None
    surname: str | None


class UserShort(UserInit, IdMixin):
    pass
