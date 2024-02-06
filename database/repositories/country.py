from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Country
from database.repositories.base import GenericRepository, GenericSqlRepository


class CountryRepositoryBase(GenericRepository[Country], ABC):
    @abstractmethod
    async def get_by_code(self, code) -> Country | None:
        raise NotImplementedError()


class CountryRepository(GenericSqlRepository[Country], CountryRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Country)

    async def get_by_code(self, code) -> Country | None:
        stmt = select(Country).where(Country.code == code)
        record = await self._session.execute(stmt)
        return record.scalar_one_or_none()
