from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class PhoneKey(Base):
    __tablename__ = 'phone_key'

    key: Mapped[str] = mapped_column(unique=True, nullable=False)

    phone: Mapped[str] = mapped_column(nullable=False)

    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    verified_at: Mapped[datetime] = mapped_column(nullable=True)
    used_at: Mapped[datetime] = mapped_column(nullable=True)

    @property
    def is_active(self):
        return self.is_verified and (not self.is_used) and self.expires_at > datetime.utcnow()
