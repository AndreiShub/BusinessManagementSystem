from fastapi import HTTPException
from app.core.meeting_permissions import ensure_team_member
from app.db.models.meeting import Meeting
from app.repositories.meeting import MeetingRepository


class MeetingService:
    def __init__(self, repo: MeetingRepository):
        self.repo = repo

    async def create_meeting(self, session, team_id, data, current_user):
        # Проверка команды
        await ensure_team_member(session, team_id, current_user.id)

        # Валидация времени
        if data.start_time >= data.end_time:
            raise HTTPException(400, "Некорректное время")

        participant_ids = set(data.participant_ids)
        participant_ids.add(current_user.id)

        # Проверка участников
        for user_id in participant_ids:
            await ensure_team_member(session, team_id, user_id)

        # Проверка пересечений
        overlap = await self.repo.check_overlap(
            session,
            team_id,
            participant_ids,
            data.start_time,
            data.end_time,
        )

        if overlap:
            raise HTTPException(400, "Пересечение встреч в команде")

        # Создание встречи
        meeting = Meeting(
            title=data.title,
            start_time=data.start_time,
            end_time=data.end_time,
            team_id=team_id,
            creator_id=current_user.id,
        )

        meeting = await self.repo.create(session, meeting)

        await self.repo.add_participants(session, meeting.id, participant_ids)

        await session.commit()

        return await self.repo.get_with_participants(session, meeting.id)

    async def get_team_meetings(self, session, team_id, current_user):
        await ensure_team_member(session, team_id, current_user.id)

        return await self.repo.get_team_meetings(
            session,
            team_id,
            current_user.id,
        )

    async def cancel_meeting(self, session, team_id, meeting_id, current_user):
        meeting = await self.repo.get_by_id(session, meeting_id)

        if not meeting or meeting.team_id != team_id:
            raise HTTPException(404, "Встреча не найдена")

        if meeting.creator_id != current_user.id:
            raise HTTPException(403, "Недостаточно прав")

        await self.repo.cancel(session, meeting)

        return {"status": "cancelled"}

    async def get_meeting(self, session, team_id, meeting_id, current_user):
        await ensure_team_member(session, team_id, current_user.id)

        meeting = await self.repo.get_with_participants(session, meeting_id)

        if not meeting or meeting.team_id != team_id:
            raise HTTPException(404, "Встреча не найдена или нет доступа")

        # проверка доступа (участник)
        if current_user.id not in [p.user_id for p in meeting.participants]:
            raise HTTPException(403, "Нет доступа")

        return meeting
