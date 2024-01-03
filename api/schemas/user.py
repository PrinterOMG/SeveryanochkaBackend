from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    first_name: str | None
    last_name: str | None
    phone: str = Field(regex=r'^\+7\d{10}$')

    class Config:
        orm_mode = True


class UserRead(UserBase):
    id: int
    created_at: datetime
    is_superuser: bool


class UserUpdate(UserBase):
    first_name: str | None
    last_name: str | None
    phone: Annotated[str | None, Field(regex=r'^\+7\d{10}$', description='For phone update phone key is required')]


class UserCheckResult(BaseModel):
    success: bool
