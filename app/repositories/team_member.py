from sqlalchemy import select
from app.db.models.user import User
from app.db.models.team import Team
from app.db.models.team_member import TeamMember


class TeamMemberRepository:
    async def get_team_by_code(self, session, code: str):
        result = await session.execute(select(Team).where(Team.code == code))
        return result.scalar_one_or_none()

    async def get_membership(self, session, team_id, user_id):
        result = await session.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_member(self, session, member: TeamMember):
        session.add(member)
        await session.commit()

    async def get_team_members(self, session, team_id):
        result = await session.execute(
            select(TeamMember, User)
            .join(User, User.id == TeamMember.user_id)
            .where(TeamMember.team_id == team_id)
        )
        return result.all()
