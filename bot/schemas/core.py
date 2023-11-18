from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    """
    В этой модели будут выполняться базовые настройки для выдаваемых данных

    (например, нужно будет выдавать данные в CamelCase и здесь вы определите alias generator)
    """
    model_config = ConfigDict(from_attributes=True)
    pass


class IdMixin(Model):
    id: int
