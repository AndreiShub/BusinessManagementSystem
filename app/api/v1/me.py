from fastapi import APIRouter, Depends
from app.db.user_db import get_user_db
from app.core.auth import fastapi_users
from app.dependencies.services import get_me_service
from app.schemas.users import UserUpdate
from app.services.me import MeService

router = APIRouter(tags=["events"])


@router.patch("/users/me")
async def update_me(
    user_update: UserUpdate,
    user=Depends(fastapi_users.current_user()),
    user_db=Depends(get_user_db),
    service: MeService = Depends(get_me_service),
):
    return await service.update_me(user_update, user, user_db)
