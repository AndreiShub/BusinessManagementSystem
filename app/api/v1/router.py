from fastapi import APIRouter
from app.core.auth import fastapi_users, auth_backend

from app.schemas.users import UserRead, UserCreate, UserUpdate
from app.api.v1.teams import router as teams_router
from app.api.v1.team_members import router as team_members_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.meetings import router as meetings_router
from app.api.v1.events import router as events_router
from app.api.v1.me import router as me_router

router = APIRouter(prefix="/api/v1")

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

router.include_router(teams_router)

router.include_router(team_members_router)

router.include_router(tasks_router)

router.include_router(meetings_router)

router.include_router(events_router)

router.include_router(me_router)
