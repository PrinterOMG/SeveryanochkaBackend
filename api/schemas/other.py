from pydantic import BaseModel


class Message(BaseModel):
    message: str


class ErrorMessage(BaseModel):
    detail: str
