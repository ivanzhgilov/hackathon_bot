import logging

from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.admin_password import AdminPassword
from utils.utils import to_snake


class AdminPasswordRepository:

    def __init__(self):
        self.logger = logging.getLogger(to_snake(self.__class__.__name__))

    async def create_point(self, session: AsyncSession, data: AdminPassword):
        self.logger.debug(f'creating point: {data}')
        command = models.AdminPassword(**data.model_dump())
        session.add(command)
        await session.flush([command])


password_repository = AdminPasswordRepository()
