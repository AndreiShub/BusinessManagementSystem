import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MeetingCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    participant_ids: list[uuid.UUID]

class ParticipantOut(BaseModel):
    id: uuid.UUID
    email: str
    nickname: str

    model_config = ConfigDict(from_attributes=True)

class MeetingParticipantOut(BaseModel):
    user: ParticipantOut

    model_config = ConfigDict(from_attributes=True)

class MeetingOut(BaseModel):
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    is_cancelled: bool

    participants: list[MeetingParticipantOut]

    class Config:
        from_attributes = True
