from datetime import datetime, timezone
import uuid
from fastapi import HTTPException
from app.repositories.event import EventRepository
from typing import List

from app.schemas.event import EventBase, MeetingEventDetail, TaskEventDetail


class EventService:
    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def get_events(self, session, user, year=None, month=None) -> List[EventBase]:
        today = datetime.now(timezone.utc)
        year = year or today.year
        month = month or today.month

        start = datetime(year, month, 1, tzinfo=timezone.utc)
        end = (
            datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            if month == 12
            else datetime(year, month + 1, 1, tzinfo=timezone.utc)
        )

        events = []

        # ===== TASKS =====
        tasks = await self.repo.get_user_tasks_in_range(session, user.id, start, end)

        for task in tasks:
            assignees = await self.repo.get_task_assignees(session, task.id)

            events.append(
                EventBase(
                    id=str(task.id),
                    title=task.title,
                    description=task.description or "",
                    event_type="task",
                    date=task.deadline.date().isoformat(),
                    time=task.deadline.strftime("%H:%M"),
                    status=task.status.value if task.status else None,
                    team_id=str(task.team_id) if task.team_id else None,
                    assignee_ids=[str(uid) for uid in assignees],
                )
            )

        # ===== MEETINGS =====
        meetings = await self.repo.get_user_meetings_in_range(
            session, user.id, start, end
        )

        now = datetime.now(timezone.utc)

        for meeting in meetings:
            if meeting.is_cancelled:
                status = "cancelled"
            elif meeting.start_time <= now <= meeting.end_time:
                status = "in_progress"
            else:
                status = "planned"

            events.append(
                EventBase(
                    id=f"meeting:{meeting.id}",
                    title=meeting.title,
                    description="Встреча",
                    event_type="meeting",
                    date=meeting.start_time.date().isoformat(),
                    time=meeting.start_time.strftime("%H:%M"),
                    status=status,
                    team_id=str(meeting.team_id),
                    assignee_ids=[str(p.user_id) for p in meeting.participants],
                )
            )

        events.sort(key=lambda e: (e.date, e.time or ""))

        return events

    async def get_event_details(self, session, event_id, user):
        # ===== MEETING =====
        if event_id.startswith("meeting:"):
            meeting_id = int(event_id.split(":")[1])

            meeting = await self.repo.get_meeting_for_user(session, meeting_id, user.id)

            if not meeting:
                raise HTTPException(404, "Meeting not found")

            now = datetime.now(timezone.utc)

            if meeting.is_cancelled:
                status = "cancelled"
            elif meeting.start_time <= now <= meeting.end_time:
                status = "in_progress"
            else:
                status = "planned"

            return MeetingEventDetail(
                id=event_id,
                title=meeting.title,
                description="Встреча",
                start_time=meeting.start_time.isoformat(),
                end_time=meeting.end_time.isoformat(),
                event_type="meeting",
                status=status,
                team_id=str(meeting.team_id),
                participants=[str(p.user_id) for p in meeting.participants],
            )

        # ===== TASK =====
        try:
            task_id = uuid.UUID(event_id)
        except ValueError:
            raise HTTPException(400, "Invalid event ID")

        task = await self.repo.get_task_by_id(session, task_id)

        if not task:
            raise HTTPException(404, "Task not found")

        return TaskEventDetail(
            id=str(task.id),
            title=task.title,
            description=task.description or "",
            deadline=task.deadline.isoformat() if task.deadline else None,
            status=task.status.value,
            event_type="task",
            team_id=str(task.team_id),
        )
