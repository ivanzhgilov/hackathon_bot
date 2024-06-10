from schemas.core import Model


class Command(Model):
    name: str
    chat_id: int