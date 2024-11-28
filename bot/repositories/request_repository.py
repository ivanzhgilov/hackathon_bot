import logging
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import Request
from schemas.request import RequestScheme
from schemas.user import UserInit
from utils.utils import to_snake


class RequestRepository:
    """
    Отвечает за работу с данными пользователя
    """

    def __init__(self):
        self.logger = logging.getLogger(to_snake(self.__class__.__name__))

    async def create_request(self, session: AsyncSession, data: UserInit) -> RequestScheme:
        self.logger.debug(f'creating request: {data}')
        request = Request(**data.model_dump())
        session.add(request)
        await session.flush([request])

        return RequestScheme.model_validate(request)

    async def get_requests_by_user(self, session: AsyncSession, user_id: int) -> List[Request]:
        self.logger.debug(f'Fetching requests for user with ID: {user_id}')
        result = await session.scalars(select(Request).where(Request.user_id == user_id))
        requests = result.all()
        if not requests:
            self.logger.debug(f'No requests found for user with ID: {user_id}')
            return []
        self.logger.info(f'Found requests for user with ID {user_id}: {requests}')
        return list(requests)

    async def delete_request_by_id(self, session: AsyncSession, request_id: int) -> bool:
        self.logger.debug(f'Deleting request with ID: {request_id}')

        # Check if the request exists
        result = await session.scalars(select(Request).where(Request.id == request_id))
        request = result.first()

        if not request:
            self.logger.debug(f'No request found with ID: {request_id}')
            return False

        # Delete the request
        await session.execute(delete(Request).where(Request.id == request_id))
        await session.commit()

        self.logger.info(f'Request with ID {request_id} has been deleted')
        return True


request_repository = RequestRepository()
