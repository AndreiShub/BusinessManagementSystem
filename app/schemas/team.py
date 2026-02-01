import uuid
from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str


class TeamRead(BaseModel):
    id: uuid.UUID
    name: str
    code: str

    class Config:
        from_attributes = True
