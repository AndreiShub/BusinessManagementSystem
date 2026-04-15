from app.db.models.team import Team
from app.db.models.team_member import TeamMember
from sqlalchemy.future import select


class TeamRepository:
    async def create(self, session, team: Team):
        session.add(team)
        await session.flush()
        return team

    async def add_member(self, session, member: TeamMember):
        session.add(member)

    async def commit(self, session):
        await session.commit()

    async def get_user_teams(self, session, user_id):
        result = await session.execute(
            select(Team).join(TeamMember).where(TeamMember.user_id == user_id)
        )
        return result.scalars().all()

    async def get_team_by_id(self, session, team_id):
        result = await session.execute(select(Team).where(Team.id == team_id))
        return result.scalar_one_or_none()
