from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    phone: str
    created_at: datetime
    is_superuser: bool

    class Config:
        orm_mode = True


class UserRead(UserBase):
    pass


class UserUpdate(UserBase):
    pass
