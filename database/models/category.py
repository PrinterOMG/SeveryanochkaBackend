from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from database.base import Base


class Category(Base):
    __tablename__ = 'category'

    name: Mapped[str] = mapped_column(nullable=False)

    parent_id: Mapped[int] = mapped_column(sa.BigInteger, ForeignKey('category.id'), nullable=True)

    parent: Mapped['Category'] = relationship('Category', back_populates='child', remote_side='[Category.id]')
    child: Mapped[list['Category']] = relationship('Category', back_populates='parent')
