from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class BrandBase(BaseModel):
    name: str


class BrandRead(BrandBase):
    id: UUID


class BrandCreate(BrandBase):
    name: Annotated[str, Field(min_length=3)]


class BrandUpdate(BrandBase):
    name: Annotated[str, Field(min_length=3)]
