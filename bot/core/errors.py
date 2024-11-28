from typing import Any


class ObjectNotExists(Exception):
    def __init__(self, message: str = "Failed to find object", identity: Any = None, entity: str = None):
        super().__init__(message)
        self.message = message
        self.identity = identity
        self.entity = entity

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.message}", identity={self.identity},entity={self.entity})'


api_errors = \
    {
        "ERROR_SESSION_TOKEN_INVALID": "Токен сеанса не действителен, авторизуйтес снова",
        "ERROR_GLPI_LOGIN": "Неправильное имя пользователя или пароль",
        "ERROR_LOGIN_PARAMETERS_MISSING": "Не указан логин или пароль",
    }
