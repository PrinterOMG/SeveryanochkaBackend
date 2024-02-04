from sqlalchemy.orm import mapped_column, Mapped
import sqlalchemy as sa

from database.base import Base


class Country(Base):
    __tablename__ = 'country'

    code: Mapped[str] = mapped_column(sa.String(2), index=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
