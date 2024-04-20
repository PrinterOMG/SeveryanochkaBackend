from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Brand(Base):
    __tablename__ = 'brand'

    name: Mapped[str] = mapped_column(index=True)

    def __repr__(self):
        return f'<Brand: id={self.id} name={self.name}>'
