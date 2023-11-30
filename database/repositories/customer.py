from abc import abstractmethod, ABC
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Customer
from database.repositories.base import GenericRepository, GenericSqlRepository


class CustomerRepositoryBase(GenericRepository[Customer], ABC):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        raise NotImplementedError()


class CustomerRepository(GenericSqlRepository[Customer], CustomerRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.name == phone)
        record = await self._session.execute(stmt)
        return record.scalar_one_or_none()
