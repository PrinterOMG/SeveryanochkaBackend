from typing import Annotated

from pydantic import BaseModel, Field


class ManufacturerBase(BaseModel):
    name: str


class ManufacturerRead(ManufacturerBase):
    id: int


class ManufacturerCreate(ManufacturerBase):
    name: Annotated[str, Field(min_length=3)]


class ManufacturerUpdate(ManufacturerBase):
    name: Annotated[str, Field(min_length=3)]
