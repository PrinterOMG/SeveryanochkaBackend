from uuid import UUID

from pydantic import BaseModel


class CountryBase(BaseModel):
    code: str
    name: str


class CountryRead(CountryBase):
    id: UUID
