from typing import List, Optional
from app.db.session import get_db
from fastapi import APIRouter, Depends, Query
from app.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import current_active_user
from app.dependencies.services import get_event_service
from app.schemas.event import EventBase, EventDetail
from app.services.event import EventService

router = APIRouter(tags=["events"])


@router.get("/events", response_model=List[EventBase])
async def get_events(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    service: EventService = Depends(get_event_service),
):
    return await service.get_events(db, user, year, month)


@router.get("/events/{event_id}", response_model=EventDetail)
async def get_event_details(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    service: EventService = Depends(get_event_service),
):
    return await service.get_event_details(db, event_id, user)
