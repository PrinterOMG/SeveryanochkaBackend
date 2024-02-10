from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Manufacturer
from database.repositories.base import GenericRepository, GenericSqlRepository


class ManufacturerRepositoryBase(GenericRepository[Manufacturer], ABC):
    pass


class ManufacturerRepository(GenericSqlRepository[Manufacturer], ManufacturerRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Manufacturer)
