from datetime import datetime

from pydantic import BaseModel, Field

from api.schemas.user import UserRead


class TokenData(BaseModel):
    user_id: int | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default='bearer')


class RegisterRequest(BaseModel):
    phone_key: str = Field(title='Phone key', description='Must be valid verified phone key')
    password: str


class RegisterResult(BaseModel):
    user: UserRead
    token: Token
