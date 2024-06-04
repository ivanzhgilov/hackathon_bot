from schemas.core import Model


class Command(Model):
    name: str
    user: str