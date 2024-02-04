from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from database.base import Base


class Product(Base):
    __tablename__ = 'product'

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    price: Mapped[float] = mapped_column(sa.DECIMAL, CheckConstraint('price > 0'), nullable=False)
    original_price: Mapped[float] = mapped_column(sa.DECIMAL, CheckConstraint('original_price > 0'), nullable=False)
    discount: Mapped[float] = mapped_column(sa.DECIMAL, CheckConstraint('discount >= 0'), nullable=False)

    stock: Mapped[float] = mapped_column(sa.DECIMAL, CheckConstraint('stock >= 0'), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)

    volume: Mapped[float] = mapped_column(sa.Float, nullable=False)
    volume_type: Mapped[str] = mapped_column(
        ENUM('items', 'g', 'kg', 'l', name='volume_types_enum'), nullable=False
    )

    brand_id: Mapped[int] = mapped_column(sa.BigInteger, ForeignKey('brand.id'), nullable=True)
    manufacturing_country_id: Mapped[int] = mapped_column(sa.BigInteger, ForeignKey('country.id'), nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(sa.BigInteger, ForeignKey('manufacturer.id'), nullable=True)
    category_id: Mapped[int] = mapped_column(sa.BigInteger, ForeignKey('category.id'), nullable=False)

    brand: Mapped['Brand'] = relationship('Brand', backref='products')
    manufacturer: Mapped['Manufacturer'] = relationship('Manufacturer', backref='products')
    manufacturing_country: Mapped['Country'] = relationship('Country', backref='products')
    category: Mapped['Category'] = relationship('Category', backref='products')
