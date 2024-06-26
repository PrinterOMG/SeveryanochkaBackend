import uuid
from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator

from core.entities.base import BaseEntity
from core.exceptions.category import CategoryCantBeItsOwnParent


class CategoryEntity(BaseEntity):
    id: Annotated[UUID, Field(default_factory=uuid.uuid4)]
    name: str
    parent_id: UUID | None

    child: list['CategoryEntity'] | None = None

    @model_validator(mode='after')
    def check_parent_id(self):
        if self.id == self.parent_id:
            raise CategoryCantBeItsOwnParent

        return self
