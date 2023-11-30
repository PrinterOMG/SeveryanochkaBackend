from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Customer(Base):
    __tablename__ = 'customer'

    name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
