from uuid import UUID

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str


class CategoryRead(CategoryBase):
    id: UUID

    parent_id: UUID | None
    child: list['CategoryRead']


class CategoryCreate(CategoryBase):
    parent_id: UUID | None


class CategoryUpdate(CategoryBase):
    name: str
    parent_id: UUID | None
