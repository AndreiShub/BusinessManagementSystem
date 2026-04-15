from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.meeting import Meeting
from app.db.models.meeting import MeetingParticipant


class MeetingRepository:
    async def create(self, session, meeting: Meeting):
        session.add(meeting)
        await session.flush()
        return meeting

    async def add_participants(self, session, meeting_id, user_ids):
        for user_id in user_ids:
            session.add(
                MeetingParticipant(
                    meeting_id=meeting_id,
                    user_id=user_id,
                )
            )

    async def check_overlap(self, session, team_id, participant_ids, start, end):
        stmt = (
            select(Meeting)
            .join(MeetingParticipant)
            .where(
                Meeting.team_id == team_id,
                MeetingParticipant.user_id.in_(participant_ids),
                Meeting.is_cancelled.is_(False),
                Meeting.start_time < end,
                Meeting.end_time > start,
            )
        )
        return await session.scalar(stmt)

    async def get_with_participants(self, session, meeting_id):
        stmt = (
            select(Meeting)
            .options(
                selectinload(Meeting.participants).selectinload(MeetingParticipant.user)
            )
            .where(Meeting.id == meeting_id)
        )
        return await session.scalar(stmt)

    async def get_team_meetings(self, session, team_id, user_id):
        stmt = (
            select(Meeting)
            .options(
                selectinload(Meeting.participants).selectinload(MeetingParticipant.user)
            )
            .join(MeetingParticipant)
            .where(
                Meeting.team_id == team_id,
                MeetingParticipant.user_id == user_id,
                Meeting.is_cancelled.is_(False),
            )
            .order_by(Meeting.start_time)
        )
        result = await session.scalars(stmt)
        return result.all()

    async def get_by_id(self, session, meeting_id):
        return await session.get(Meeting, meeting_id)

    async def cancel(self, session, meeting: Meeting):
        meeting.is_cancelled = True
        await session.commit()
