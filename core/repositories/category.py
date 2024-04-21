from abc import ABC, abstractmethod

from sqlalchemy import select, update

from core.entities.category import CategoryEntity
from core.exceptions.base import EntityNotFoundError
from core.repositories.base import GenericRepository, GenericSARepository, T
from database.base import Base
from database.models import Category


class CategoryRepositoryBase(GenericRepository[CategoryEntity], ABC):
    entity = CategoryEntity

    @abstractmethod
    async def get_root_categories(self, depth: int) -> list[CategoryEntity]:
        raise NotImplementedError


class SACategoryRepository(GenericSARepository, CategoryRepositoryBase):
    model_cls = Category

    async def _convert_to_entity_with_depth(self, category: Category, depth: int = 0, cur_depth=0) -> CategoryEntity:
        if cur_depth >= depth:
            sub_categories = []
        else:
            sub_categories = [
                await self._convert_to_entity_with_depth(sub_category, depth, cur_depth + 1)
                for sub_category in await category.awaitable_attrs.child
            ]

        return CategoryEntity(
            id=category.id,
            name=category.name,
            parent_id=category.parent_id,
            child=sub_categories
        )

    async def _convert_db_to_entity(self, record: Category, **kwargs) -> T:
        return await self._convert_to_entity_with_depth(record, **kwargs)
    
    async def _convert_entity_to_update_dict(self, entity: CategoryEntity, **kwargs) -> dict:
        return entity.model_dump(exclude={'id', 'child'})
    
    async def _convert_entity_to_db(self, entity: CategoryEntity, **kwargs) -> Base:
        return self.model_cls(**entity.model_dump(exclude={'child'}))

    async def get_root_categories(self, depth: int) -> list[CategoryEntity]:
        stmt = select(Category).where(Category.parent_id == None)
        records = await self._session.scalars(stmt)

        categories = records.all()

        return [await self._convert_db_to_entity(category, depth=depth) for category in categories]
