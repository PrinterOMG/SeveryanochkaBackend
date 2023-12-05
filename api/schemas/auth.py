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


class VerifyPhoneKey(BaseModel):
    key: str = Field(
        title='Phone key',
        description='Phone key that was '
    )
    code: str = Field(
        title='Confirmation code',
        description='Four-digit confirmation code that was sent to the user\'s phone number',
        regex=r'[0-9]{4}'
    )


class CreatePhoneKey(BaseModel):
    phone: str = Field(
        regex=r'^\+7\d{10}$',
        title='Phone number',
        description='Phone number to create a key. The number must start with +7 and consist of 11 digits.'
    )


class PhoneKeyRead(BaseModel):
    key: str
    phone: str = Field(regex=r'^\+7\d{10}$')
    created_at: datetime
    expires_at: datetime
    is_verified: bool

    class Config:
        orm_mode = True
