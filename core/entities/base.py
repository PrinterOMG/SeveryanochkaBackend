import uuid
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: Annotated[UUID, Field(default_factory=uuid.uuid4)]
