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


class JoinTeamRequest(BaseModel):
    code: str


class TeamMemberRead(BaseModel):
    user_id: uuid.UUID
    role: str

    class Config:
        from_attributes = True
