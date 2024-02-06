from pydantic import BaseModel


class CountryBase(BaseModel):
    code: str
    name: str


class CountryRead(CountryBase):
    id: int
