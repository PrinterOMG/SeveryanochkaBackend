from datetime import datetime, date
from typing import Annotated

from pydantic import Field

from core.entities.base import BaseEntity


class UserEntity(BaseEntity):
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    avatar_url: str | None = None
    phone: str
    hashed_password: str
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow)]
    is_superuser: bool
