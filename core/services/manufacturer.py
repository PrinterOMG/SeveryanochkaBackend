from abc import abstractmethod, ABC
from uuid import UUID

from api.schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate
from core.entities.manufacturer import ManufacturerEntity
from core.repositories.manufacturer import ManufacturerRepositoryBase
from core.unit_of_work import UnitOfWorkBase


class ManufacturerServiceBase(ABC):
    def __init__(
            self,
            manufacturer_repository: ManufacturerRepositoryBase,
            uow: UnitOfWorkBase,
    ):
        self.manufacturer_repository = manufacturer_repository
        self.uow = uow

    @abstractmethod
    async def get_by_id(self, manufacturer_id: UUID) -> ManufacturerEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> list[ManufacturerEntity]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, manufacturer: ManufacturerCreate) -> ManufacturerEntity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, manufacturer_id: UUID, update_data: ManufacturerUpdate) -> ManufacturerEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, manufacturer_id: UUID) -> None:
        raise NotImplementedError


class ManufacturerService(ManufacturerServiceBase):
    async def get_all(self, limit: int, offset: int) -> list[ManufacturerEntity]:
        return await self.manufacturer_repository.list(offset=offset, limit=limit)

    async def create(self, manufacturer: ManufacturerCreate) -> ManufacturerEntity:
        entity = ManufacturerEntity.model_validate(manufacturer)
        new_manufacturer = await self.manufacturer_repository.add(entity)
        await self.uow.commit()
        return new_manufacturer

    async def update(self, manufacturer_id: UUID, update_data: ManufacturerUpdate) -> ManufacturerEntity:
        entity = ManufacturerEntity(id=manufacturer_id, **update_data.model_dump())
        manufacturer = await self.manufacturer_repository.update(entity)
        await self.uow.commit()
        return manufacturer

    async def delete(self, manufacturer_id: UUID) -> None:
        await self.manufacturer_repository.delete(manufacturer_id)
        await self.uow.commit()

    async def get_by_id(self, manufacturer_id: UUID) -> ManufacturerEntity | None:
        return await self.manufacturer_repository.get_by_id(manufacturer_id)
