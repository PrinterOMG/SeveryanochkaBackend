from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Brand(Base):
    __tablename__ = 'brand'

    name: Mapped[str] = mapped_column(nullable=False, index=True)
