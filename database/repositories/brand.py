from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Brand
from database.repositories.base import GenericRepository, GenericSqlRepository


class BrandRepositoryBase(GenericRepository[Brand], ABC):
    pass


class BrandRepository(GenericSqlRepository[Brand], BrandRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Brand)
