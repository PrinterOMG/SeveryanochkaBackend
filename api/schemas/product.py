from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from api.schemas.brand import BrandRead
from api.schemas.category import CategoryRead
from api.schemas.manufacturer import ManufacturerRead


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
    id: UUID

    category: CategoryRead
    brand: BrandRead
    manufacturer: ManufacturerRead
