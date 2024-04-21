from abc import ABC, abstractmethod
from uuid import UUID

from api.schemas.category import CategoryUpdate, CategoryCreate
from core.entities.category import CategoryEntity
from core.repositories.category import CategoryRepositoryBase
from core.unit_of_work import UnitOfWorkBase


class CategoryServiceBase(ABC):
    def __init__(
            self,
            category_repository: CategoryRepositoryBase,
            uow: UnitOfWorkBase,
    ):
        self.category_repository = category_repository
        self.uow = uow

    @abstractmethod
    async def get_by_id(self, category_id: UUID, depth: int) -> CategoryEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_root_categories(self, depth: int) -> list[CategoryEntity]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, category_id: UUID, data: CategoryUpdate) -> CategoryEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, category_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: CategoryCreate) -> CategoryEntity:
        raise NotImplementedError


class CategoryService(CategoryServiceBase):
    async def get_by_id(self, category_id: UUID, depth: int) -> CategoryEntity:
        return await self.category_repository.get_by_id(category_id, depth=depth)

    async def get_root_categories(self, depth: int) -> list[CategoryEntity]:
        return await self.category_repository.get_root_categories(depth)

    async def update(self, category_id: UUID, data: CategoryUpdate) -> CategoryEntity:
        category = await self.category_repository.update(
            CategoryEntity(id=category_id, **data.model_dump()),
            depth=0
        )
        await self.uow.commit()
        return category

    async def delete(self, category_id: UUID) -> None:
        await self.category_repository.delete(category_id)
        await self.uow.commit()

    async def create(self, data: CategoryCreate) -> CategoryEntity:
        category = CategoryEntity(**data.model_dump())
        category = await self.category_repository.add(category)
        await self.uow.commit()
        return category
