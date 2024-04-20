from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Manufacturer(Base):
    __tablename__ = 'manufacturer'

    name: Mapped[str] = mapped_column()
