from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Category(Base):
    __tablename__ = 'category'

    name: Mapped[str] = mapped_column()

    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey('category.id'))

    parent: Mapped['Category'] = relationship(back_populates='child', remote_side='[Category.id]')
    child: Mapped[list['Category']] = relationship(back_populates='parent')
