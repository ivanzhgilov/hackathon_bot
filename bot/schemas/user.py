from core.constants import UserRole
from schemas.core import Model, IdMixin


class UserInit(Model):
    chat_id: int
    login: str
    name: str | None
    surname: str | None
    admin: bool


class UserAbout(Model):
    role: UserRole
    about: str
    target: str


class UserShort(UserInit, IdMixin):
    about: UserAbout | None
