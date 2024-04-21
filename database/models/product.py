from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from database.base import Base


if TYPE_CHECKING:
    from database.models import Brand, Manufacturer, Country, Category


class Product(Base):
    __tablename__ = 'product'

    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    price: Mapped[float] = mapped_column(sa.DECIMAL, CheckConstraint('price > 0'))
    original_price: Mapped[float] = mapped_column(
        sa.DECIMAL, CheckConstraint('original_price > 0')
    )
    discount: Mapped[float] = mapped_column(
        sa.DECIMAL, CheckConstraint('discount >= 0')
    )

    stock: Mapped[float] = mapped_column(sa.DECIMAL, CheckConstraint('stock >= 0'))
    is_active: Mapped[bool] = mapped_column()

    volume: Mapped[float] = mapped_column(sa.Float)
    volume_type: Mapped[str] = mapped_column(
        ENUM('items', 'g', 'kg', 'l', name='volume_types_enum')
    )

    brand_id: Mapped[UUID | None] = mapped_column(ForeignKey('brand.id'))
    manufacturing_country_id: Mapped[UUID] = mapped_column(ForeignKey('country.id'))
    manufacturer_id: Mapped[UUID | None] = mapped_column(ForeignKey('manufacturer.id'))
    category_id: Mapped[UUID] = mapped_column(ForeignKey('category.id'))

    # TODO: поменять на back_populates
    brand: Mapped['Brand'] = relationship(backref='products')
    manufacturer: Mapped['Manufacturer'] = relationship(backref='products')
    manufacturing_country: Mapped['Country'] = relationship(backref='products')
    category: Mapped['Category'] = relationship(backref='products')
