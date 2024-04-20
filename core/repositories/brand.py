from abc import ABC

from core.entities.brand import BrandEntity
from core.repositories.base import GenericRepository, GenericSARepository
from database.models import Brand


class BrandRepositoryBase(GenericRepository[BrandEntity], ABC):
    entity = BrandEntity


class SABrandRepository(GenericSARepository, BrandRepositoryBase):
    model_cls = Brand
