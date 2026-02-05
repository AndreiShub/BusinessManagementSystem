from fastapi import FastAPI
from app.api.v1.router import router as api_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.web.router import router as web_router
from app.admin import setup_admin
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

app = FastAPI(
    title="Business Management System",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(api_router)
app.include_router(web_router)

setup_admin(app)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
