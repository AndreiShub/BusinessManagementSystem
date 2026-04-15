import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.team_member import TeamMember
from tests.factories.task_factory import create_task
from tests.factories.team_factory import create_team
from tests.factories.user_factory import create_user


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, db_session: AsyncSession, auth_headers):
    # создаем пользователя и команду
    user = await create_user(db_session)
    team = await create_team(db_session, creator=user)
    member = TeamMember(
        team_id=team.id,
        user_id=user.id,
    )

    db_session.add(member)
    await db_session.commit()
    # создаем задачу через фабрику
    task = await create_task(db_session, team_id=team.id, creator_id=user.id)

    response = await client.get(f"/api/v1/teams/{team.id}/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == task.title


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, db_session: AsyncSession, auth_headers):
    user = await create_user(db_session)
    team = await create_team(db_session, creator=user)
    task = await create_task(db_session, team_id=team.id, creator_id=user.id)

    response = await client.get(
        f"/api/v1/teams/{team.id}/tasks/{task.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task.title


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, db_session: AsyncSession, auth_headers):
    user = await create_user(db_session)
    team = await create_team(db_session, creator=user)
    member = TeamMember(
        team_id=team.id,
        user_id=user.id,
    )

    db_session.add(member)
    await db_session.commit()
    payload = {
        "title": "New Task",
        "description": "Task Description",
        "deadline": None,
        "assignee_id": str(user.id),
    }

    response = await client.post(
        f"/api/v1/teams/{team.id}/tasks", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Task"
    assert str(user.id) in [str(aid) for aid in data.get("assignee_ids", [])]


@pytest.mark.asyncio
async def test_update_task_status_only(
    client: AsyncClient, db_session: AsyncSession, auth_headers
):
    user = await create_user(db_session)
    team = await create_team(db_session, creator=user)
    task = await create_task(db_session, team_id=team.id, creator_id=user.id)

    payload = {"status": "done"}
    response = await client.patch(
        f"/api/v1/teams/{team.id}/tasks/{task.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, db_session: AsyncSession, auth_headers):
    user = await create_user(db_session)
    team = await create_team(db_session, creator=user)
    member = TeamMember(
        team_id=team.id,
        user_id=user.id,
    )

    db_session.add(member)
    await db_session.commit()
    task = await create_task(db_session, team_id=team.id, creator_id=user.id)

    response = await client.delete(
        f"/api/v1/teams/{team.id}/tasks/{task.id}", headers=auth_headers
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_rate_task(client: AsyncClient, db_session: AsyncSession, auth_headers):
    user = await create_user(db_session)
    team = await create_team(db_session, creator=user)
    task = await create_task(db_session, team_id=team.id, creator_id=user.id)

    payload = {"score": 5}
    response = await client.post(
        f"/api/v1/teams/{team.id}/tasks/{task.id}/rating",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_add_comment(client: AsyncClient, db_session: AsyncSession, auth_headers):
    user = await create_user(db_session)
    team = await create_team(db_session, creator=user)
    task = await create_task(db_session, team_id=team.id, creator_id=user.id)

    payload = {"text": "Nice work!"}
    response = await client.post(
        f"/api/v1/teams/{team.id}/tasks/{task.id}/comments",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Nice work!"
    assert data["nickname"] == user.nickname
