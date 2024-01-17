from datetime import datetime, date

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    first_name: str | None
    last_name: str | None
    birthday: date | None

    class Config:
        from_attributes = True


class UserRead(UserBase):
    id: int
    created_at: datetime
    is_superuser: bool
    phone: str = Field(pattern=r'^\+7\d{10}$')


class UserUpdate(UserBase):
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None


class UserCheckResult(BaseModel):
    success: bool
