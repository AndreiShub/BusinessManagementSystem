import uuid
from datetime import datetime
from pydantic import BaseModel


class MeetingCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    participant_ids: list[uuid.UUID]


class MeetingParticipantOut(BaseModel):
    id: uuid.UUID
    email: str
    nickname: str

    class Config:
        from_attributes = True


class MeetingOut(BaseModel):
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    is_cancelled: bool

    participants: list[MeetingParticipantOut]

    class Config:
        from_attributes = True
