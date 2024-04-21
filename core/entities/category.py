from uuid import UUID

from core.entities.base import BaseEntity


class CategoryEntity(BaseEntity):
    name: str
    parent_id: UUID | None
    
    child: list["CategoryEntity"] | None = None
