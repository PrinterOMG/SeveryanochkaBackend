from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.product import ProductEntity
from core.repositories.base import GenericRepository, GenericSARepository


class ProductRepositoryBase(GenericRepository[ProductEntity], ABC):
    pass


class ProductSARepository(GenericSARepository[ProductEntity], ProductRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProductEntity)

