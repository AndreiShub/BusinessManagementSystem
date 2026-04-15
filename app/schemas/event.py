from pydantic import BaseModel
from typing import Optional, List, Literal, Union


class EventBase(BaseModel):
    id: str
    title: str
    description: str = ""
    event_type: Literal["task", "meeting"]
    date: Optional[str] = None
    time: Optional[str] = None
    status: Optional[str] = None
    team_id: Optional[str] = None
    assignee_ids: List[str] = []


class TaskEventDetail(BaseModel):
    event_type: Literal["task"]
    id: str
    title: str
    description: str = ""
    deadline: Optional[str]
    status: str
    event_type: Literal["task"]
    team_id: Optional[str]


class MeetingEventDetail(BaseModel):
    event_type: Literal["meeting"]
    id: str
    title: str
    description: str = ""
    start_time: str
    end_time: str
    event_type: Literal["meeting"]
    status: str
    team_id: str
    participants: List[str]


EventDetail = Union[TaskEventDetail, MeetingEventDetail]
