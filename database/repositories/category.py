from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Category
from database.repositories.base import GenericRepository, GenericSqlRepository


class CategoryRepositoryBase(GenericRepository[Category], ABC):
    pass


class CategoryRepository(GenericSqlRepository[Category], CategoryRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Category)
