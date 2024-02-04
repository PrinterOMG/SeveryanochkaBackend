from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str


class CategoryRead(CategoryBase):
    id: int

    parent_id: int | None
    child: list['CategoryRead']


class CategoryCreate(CategoryBase):
    parent_id: int | None


class CategoryUpdate(CategoryBase):
    name: str | None = None
    parent_id: int | None = None
