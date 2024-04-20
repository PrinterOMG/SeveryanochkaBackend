from abc import abstractmethod, ABC
from uuid import UUID

from core.entities.country import CountryEntity
from core.repositories.country import CountryRepositoryBase
from core.unit_of_work import UnitOfWorkBase


class CountryServiceBase(ABC):
    def __init__(
            self,
            country_repository: CountryRepositoryBase
    ):
        self.country_repository = country_repository

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> list[CountryEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, country_id: UUID) -> CountryEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_code(self, country_code: str) -> CountryEntity | None:
        raise NotImplementedError


class CountryService(CountryServiceBase):

    async def get_all(self, limit: int, offset: int) -> list[CountryEntity]:
        return await self.country_repository.list(limit=limit, offset=offset)

    async def get_by_id(self, country_id: UUID) -> CountryEntity | None:
        return await self.country_repository.get_by_id(country_id)

    async def get_by_code(self, country_code: str) -> CountryEntity | None:
        return await self.country_repository.get_by_code(country_code)
