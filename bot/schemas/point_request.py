from schemas.core import Model


class PointRequest(Model):
    title: str
    author: str
    description: str | None
    address: str
    phone_number: str | None
    types_of_garbage: str
    lat: float | None
    lon: float | None