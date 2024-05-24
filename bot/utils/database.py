import contextlib
from typing import AsyncGenerator, Tuple, Callable, AsyncContextManager

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from core.config import config

async_engine_default_params = {
    'poolclass': NullPool
}


def async_session_factory(
        async_connection_string,
        **engine_params
) -> Tuple[AsyncGenerator[AsyncSession, None], Callable[[], AsyncContextManager[AsyncSession]], AsyncEngine]:
    """
    Функция для создания асинхронной фабрики соединений с бд

    :param async_connection_string: connection url начинающийся с postgresql+asyncpg
    :param engine_params: параметры для AsyncEngine (настройки пула соединений)
    :return: генератор для использования в fastapi.Depends, контекстный менеджер
             бд для использования в любом ином месте, AsyncEngine для низкоуровнего взаимодействия
    """
    params = async_engine_default_params.copy()
    params.update(engine_params)

    engine = create_async_engine(async_connection_string, **params)

    # noinspection PyTypeChecker
    maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def get_async_session() -> AsyncSession:
        from models.user import User
        from models.admin_password import AdminPassword
        from models.core import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        try:
            sess: AsyncSession = maker()
            yield sess
        except Exception as e:
            await sess.rollback()
            raise e
        finally:
            await sess.commit()
            await sess.close()

    # noinspection PyTypeChecker
    return get_async_session, contextlib.asynccontextmanager(get_async_session), engine


db_async_session, db_async_session_manager, async_engine = async_session_factory(config.async_db_conn_str)
