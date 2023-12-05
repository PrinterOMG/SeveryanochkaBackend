from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    phone: str = Field(regex=r'^\+7\d{10}$')
    created_at: datetime
    is_superuser: bool

    class Config:
        orm_mode = True


class UserRead(UserBase):
    pass


class UserUpdate(UserBase):
    pass
