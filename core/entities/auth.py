from uuid import UUID

from pydantic import BaseModel


class TokenData(BaseModel):
    user_id: UUID | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
