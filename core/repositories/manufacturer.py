from abc import ABC

from core.entities.manufacturer import ManufacturerEntity
from core.repositories.base import GenericRepository, GenericSARepository
from database.models import Manufacturer


class ManufacturerRepositoryBase(GenericRepository[ManufacturerEntity], ABC):
    entity = ManufacturerEntity


class SAManufacturerRepository(GenericSARepository, ManufacturerRepositoryBase):
    model_cls = Manufacturer
