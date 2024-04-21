from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class PhoneKey(Base):
    __tablename__ = 'phone_key'

    key: Mapped[str] = mapped_column(unique=True)

    phone: Mapped[str] = mapped_column()

    is_verified: Mapped[bool] = mapped_column(default=False)
    is_used: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column()
    verified_at: Mapped[datetime | None] = mapped_column()
    used_at: Mapped[datetime | None] = mapped_column()

    @property
    def is_active(self):
        return (
            self.is_verified
            and (not self.is_used)
            and self.expires_at > datetime.utcnow()
        )
