from typing import Literal

from pydantic import BaseModel

from api.schemas.brand import BrandRead
from api.schemas.category import CategoryRead


class ManufacturerBase(BaseModel):
    name: str


class ManufacturerRead(ManufacturerBase):
    id: int


class ProductBase(BaseModel):
    name: str
    description: str

    price: float
    original_price: float
    discount: float

    stock: float
    is_active: bool

    volume: float
    volume_type: Literal['items', 'g', 'kg', 'l']


class ProductRead(ProductBase):
    id: int

    category: CategoryRead
    brand: BrandRead
    manufacturer: ManufacturerRead
