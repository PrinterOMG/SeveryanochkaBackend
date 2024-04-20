from abc import ABC, abstractmethod

from sqlalchemy import select

from core.entities.country import CountryEntity
from core.repositories.base import GenericRepository, GenericSARepository
from database.models import Country


class CountryRepositoryBase(GenericRepository[Country], ABC):
    entity = CountryEntity

    @abstractmethod
    async def get_by_code(self, code: str) -> CountryEntity | None:
        raise NotImplementedError()


class SACountryRepository(GenericSARepository, CountryRepositoryBase):
    model_cls = Country

    async def get_by_code(self, code: str) -> CountryEntity | None:
        stmt = select(Country).where(Country.code == code)
        record = await self._session.scalar(stmt)
        if record is None:
            return None
        return CountryEntity.model_validate(record)
