from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class ManufacturerBase(BaseModel):
    name: str


class ManufacturerRead(ManufacturerBase):
    id: UUID


class ManufacturerCreate(ManufacturerBase):
    name: Annotated[str, Field(min_length=3)]


class ManufacturerUpdate(ManufacturerBase):
    name: Annotated[str, Field(min_length=3)]
