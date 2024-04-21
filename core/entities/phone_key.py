from datetime import datetime
from typing import Annotated

from pydantic import Field

from core.entities.base import BaseEntity


class PhoneKeyEntity(BaseEntity):
    key: str
    phone: str
    is_verified: bool = False
    is_used: bool = False
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow)]
    expires_at: datetime
    verified_at: datetime | None = None
    used_at: datetime | None = None

    @property
    def is_ready_to_use(self):
        """
        The key is ready to use if it is verified, not used and not expired
        """
        return (
            self.is_verified
            and (not self.is_used)
            and self.expires_at > datetime.utcnow()
        )
