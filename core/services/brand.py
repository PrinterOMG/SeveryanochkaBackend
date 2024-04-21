from abc import ABC, abstractmethod
from uuid import UUID

from api.schemas.brand import BrandCreate, BrandUpdate
from core.entities.brand import BrandEntity
from core.repositories.brand import BrandRepositoryBase
from core.unit_of_work import UnitOfWorkBase


class BrandServiceBase(ABC):
    def __init__(
        self,
        brand_repository: BrandRepositoryBase,
        uow: UnitOfWorkBase,
    ):
        self.brand_repository = brand_repository
        self.uow = uow

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> list[BrandEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, brand_id: UUID) -> BrandEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, brand: BrandCreate) -> BrandEntity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, brand_id: UUID, brand_data: BrandUpdate) -> BrandEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, brand_id: UUID) -> None:
        raise NotImplementedError


class BrandService(BrandServiceBase):
    async def get_all(self, limit: int, offset: int) -> list[BrandEntity]:
        return await self.brand_repository.list(limit=limit, offset=offset)

    async def get_by_id(self, brand_id: UUID) -> BrandEntity | None:
        return await self.brand_repository.get_by_id(brand_id)

    async def create(self, brand: BrandCreate) -> BrandEntity:
        brand = BrandEntity.model_validate(brand)
        brand = await self.brand_repository.add(brand)
        await self.uow.commit()
        return brand

    async def update(self, brand_id: UUID, brand_data: BrandUpdate) -> BrandEntity:
        brand = BrandEntity(id=brand_id, **brand_data.model_dump())
        brand = await self.brand_repository.update(brand)
        await self.uow.commit()
        return brand

    async def delete(self, brand_id: UUID) -> None:
        await self.brand_repository.delete(brand_id)
        await self.uow.commit()
