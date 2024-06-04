import logging

from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.command import Command
from utils.utils import to_snake


class CommandRepository:

    def __init__(self):
        self.logger = logging.getLogger(to_snake(self.__class__.__name__))

    async def create_point(self, session: AsyncSession, data: Command):
        self.logger.debug(f'creating point: {data}')
        command = models.Command(**data.model_dump())
        session.add(command)
        await session.flush([command])


command_repository = CommandRepository()
