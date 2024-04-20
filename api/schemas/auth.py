from uuid import UUID

from pydantic import BaseModel, Field

from api.schemas.user import UserRead


class TokenRead(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class RegisterRequest(BaseModel):
    phone_key: str = Field(title='Phone key', description='Must be valid verified phone key')
    password: str = Field(
        title='Password',
        description='Must be between 8 and 64 characters long', min_length=8, max_length=64
    )


class RegisterResult(BaseModel):
    user: UserRead
    token: TokenRead


class ResetPasswordRequest(BaseModel):
    phone_key: str = Field(title='Phone key', description='Must be valid verified phone key')
    password: str = Field(
        title='Password',
        description='Must be between 8 and 64 characters long', min_length=8, max_length=64
    )
