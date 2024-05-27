import logging

from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.point_request import PointRequest
from utils.utils import to_snake


class PointRepository:
    """
    Отвечает за работу с данными о точках
    """

    def __init__(self):
        self.logger = logging.getLogger(to_snake(self.__class__.__name__))

    async def create_point(self, session: AsyncSession, data: PointRequest):
        self.logger.debug(f'creating point: {data}')
        point = models.PointRequest(**data.model_dump())
        session.add(point)
        await session.flush([point])


point_repository = PointRepository()
