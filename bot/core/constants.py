import enum


class UserRole(str, enum.Enum):
    frontend_developer = 'frontend_developer'
    backend_developer = 'backend_developer'
    designer = 'designer'
    dummy = 'dummy'


# перевод не занесён в значения enum'а, потому что на значения будет завязана логика приложения,
# а перевод может в любой момент поменяться
UserRoleTranslation = {
    UserRole.frontend_developer: 'frontend разработчик',
    UserRole.backend_developer: 'backend разработчик',
    UserRole.designer: 'дизайнер',
    UserRole.dummy: 'на подхвате',
}
