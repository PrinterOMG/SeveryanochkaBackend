from datetime import datetime, date

from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class User(Base):
    __tablename__ = 'user'

    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    birthday: Mapped[date | None] = mapped_column()
    avatar_url: Mapped[str | None] = mapped_column()

    phone: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_superuser: Mapped[bool] = mapped_column(default=False)
