from pydantic import BaseModel


class BrandBase(BaseModel):
    name: str


class BrandRead(BrandBase):
    id: int
