from pydantic import BaseModel


class CustomerOut(BaseModel):
    name: str
    last_name: str
    phone: str
