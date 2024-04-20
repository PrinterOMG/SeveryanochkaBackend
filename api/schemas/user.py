from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    first_name: str | None
    last_name: str | None
    birthday: date | None

    class Config:
        from_attributes = True


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    avatar_url: str | None
    is_superuser: bool
    phone: str = Field(pattern=r'^\+7\d{10}$')


class UserUpdate(UserBase):
    first_name: str | None
    last_name: str | None
    birthday: date | None


class UserCheckResult(BaseModel):
    success: bool


class SetAvatarResult(BaseModel):
    avatar_url: str
