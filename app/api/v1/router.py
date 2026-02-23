from fastapi import APIRouter, Depends
from app.core.auth import fastapi_users, auth_backend
from app.db.user_db import get_user_db
from app.schemas.users import UserRead, UserCreate, UserUpdate
from app.api.v1.teams import router as teams_router
from app.api.v1.team_members import router as team_members_router
from app.api.v1.tasks import router as tasks_router

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

@router.patch("/users/me")
async def update_me(
    user_update: UserUpdate,
    user=Depends(fastapi_users.current_user()),
    user_db=Depends(get_user_db),
):
    # обновляем только те поля, что пришли
    updated = False
    if user_update.email is not None:
        user.email = user_update.email
        updated = True
    if user_update.nickname is not None:
        user.nickname = user_update.nickname
        updated = True

    if updated:
        await user_db.update(user)

    return {
        "email": user.email,
        "nickname": user.nickname,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_manager": user.is_manager,
    }