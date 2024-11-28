import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserInit, UserAccount, UserShort
from utils.utils import to_snake, hash_password


class UserRepository:
    """
    Отвечает за работу с данными пользователя
    """

    def __init__(self):
        self.logger = logging.getLogger(to_snake(self.__class__.__name__))

    async def create_user(self, session: AsyncSession, data: UserInit) -> UserAccount:
        if existing := (await self.get_user_by_chat_id(session, data.chat_id)):
            self.logger.debug(f'User with chat_id: {data.chat_id} already exists. Skipping creation')
            return UserAccount.model_validate(existing)

        self.logger.debug(f'creating user: {data}')
        user = User(**data.model_dump())
        session.add(user)
        await session.flush([user])

        return UserAccount.model_validate(user)

    async def get_all_logins(self, session: AsyncSession) -> List[str]:
        self.logger.debug('Fetching all user logins')
        result = await session.scalars(select(User.login))
        logins = result.all()
        if not logins:
            self.logger.debug('No user logins found')
            return []
        self.logger.info(f'Found user logins: {logins}')
        return list(logins)

    async def get_user_by_chat_id(self, session: AsyncSession, chat_id: int) -> UserShort | None:
        self.logger.debug(f'fetching user with chat_id: {chat_id}')
        fetched = await session.scalar(select(User).where(User.chat_id == chat_id))
        if not fetched:
            self.logger.debug(f'user not found by chat_id: {chat_id}')
            return None
        self.logger.info(f'found by chat_id: {chat_id} - {fetched}')
        return fetched

    async def update_hashed_password_by_chat_id(self, session: AsyncSession, chat_id: int, password: str) -> bool:
        self.logger.debug(f'Updating hashed_password for user with chat_id: {chat_id}')

        user = await self.get_user_by_chat_id(session, chat_id)
        if not user:
            self.logger.debug(f'No user found with chat_id: {chat_id}')
            return False

        hashed_password = hash_password(password)

        user.hashed_password = hashed_password
        session.add(user)
        await session.flush([user])

        self.logger.info(f'Hashed password updated for user with chat_id: {chat_id}')
        return True

    async def update_login_status_by_chat_id(self, session: AsyncSession, chat_id: int, login_status: bool) -> bool:
        self.logger.debug(f'Updating login_status for user with chat_id: {chat_id}')

        # Fetch the user by chat_id
        user = await self.get_user_by_chat_id(session, chat_id)
        if not user:
            self.logger.debug(f'No user found with chat_id: {chat_id}')
            return False

        # Update the login_status
        user.login_status = login_status
        session.add(user)
        await session.flush([user])

        self.logger.info(f'Login status updated for user with chat_id: {chat_id}')
        return True

    async def update_hashed_password_by_login(self, session: AsyncSession, login: str, password: str) -> bool:
        self.logger.debug(f'Updating hashed_password for user with login: {login}')

        # Fetch the user by login
        user = await self.get_user_by_login(session, login)
        if not user:
            self.logger.debug(f'No user found with login: {login}')
            return False

        # Hash the password
        hashed_password = hash_password(password)

        # Update the hashed_password
        user.hashed_password = hashed_password
        session.add(user)
        await session.flush([user])

        self.logger.info(f'Hashed password updated for user with login: {login}')
        return True

    async def update_login_by_chat_id(self, session: AsyncSession, chat_id: int, new_login: str) -> bool:
        self.logger.debug(f'Updating login for user with chat_id: {chat_id}')

        # Fetch the user by chat_id
        user = await self.get_user_by_chat_id(session, chat_id)
        if not user:
            self.logger.debug(f'No user found with chat_id: {chat_id}')
            return False

        # Update the login
        user.login = new_login
        session.add(user)
        await session.flush([user])

        self.logger.info(f'Login updated for user with chat_id: {chat_id}')
        return True

    async def get_user_by_login(self, session: AsyncSession, login: str) -> UserShort | None:
        self.logger.debug(f'fetching user with login: {login}')
        fetched = await session.scalar(select(User).where(User.login == login))
        if not fetched:
            self.logger.debug(f'user not found by login: {login}')
            return None
        return fetched

    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> UserAccount | None:
        self.logger.debug(f'fetching user with id: {user_id}')
        fetched = await session.get(User, user_id)
        if not fetched:
            self.logger.debug(f'user not found by id: {user_id}')
            return None

        obj = UserAccount.model_validate(fetched)
        self.logger.info(f'found by id: {user_id} - {obj}')
        return obj

    # async def fill_about(self, session: AsyncSession, user_id: int, about: UserAbout):
    #     user = await self.get_user_by_id(session, user_id)
    #     if not user:
    #         raise ObjectNotExists(identity=user, entity=User.__name__)
    #
    #     await session.execute(
    #         update(User)
    #         .where(User.id == user_id)
    #         .values(about=about.model_dump(mode='json'))
    #     )


user_repository = UserRepository()  # в случае с нормальным DI, этот объект бы создавался через него в отдельном месте, а не тут
