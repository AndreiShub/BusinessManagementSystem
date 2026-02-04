import uuid
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request},
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request},
    )


@router.get("/teams")
def teams_page(request: Request):
    return templates.TemplateResponse(
        "teams.html",
        {"request": request},
    )


@router.get("/teams/{team_id}/tasks")
def tasks_page(request: Request, team_id: uuid.UUID):
    return templates.TemplateResponse(
        "tasks.html",
        {"request": request, "team_id": team_id},
    )


@router.get("/join")
async def join_page(request: Request):
    return templates.TemplateResponse("join.html", {"request": request})
