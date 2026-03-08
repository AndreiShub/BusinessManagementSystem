import uuid
from app.db.models import Team, TeamMember

async def create_team(db_session, creator, **kwargs):
    team = Team(
        id=uuid.uuid4(),
        name=kwargs.get("name", f"Team {uuid.uuid4().hex[:6]}"),
        code=kwargs.get("code", f"team_{uuid.uuid4().hex[:8]}"),
    )
    db_session.add(team)
    await db_session.flush()
    await db_session.refresh(team)

    # Добавляем создателя в команду
    member = TeamMember(team_id=team.id, user_id=creator.id)
    db_session.add(member)
    await db_session.flush()

    return team