from fastapi import FastAPI, APIRouter
from starlette.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.background.check_battle import check_battle_completion
from db.models.database import create_db_and_tables
from api.routers.video import router as video_router
from api.routers.user import router as user_router
from api.routers.battle import router as battle_router
from api.routers.tag import router as tag_router
from api.routers.telegram import router as telegram_router

from db.tools.init_system_tables import init_system_tables

tags_metadata = [
    {
        "name": "Пользователи",
        "description": "Набор методов для получения информации о пользователе"
    },
    {
        "name": "Вызовы",
        "description": "Набор методов для получения информации о текущих батлах, управления их событиями"
    },
    {
        "name": "Клипы",
        "description": "Набор методов для отображения информации о клипах"
    },
    {
        "name": "Тэги",
        "description": "Набор методов для отображения информации о тэгах клипов"
    },
    {
        "name": "Telegram",
        "description": "Методы для запросов к телеграм"
    },
]

app = FastAPI(
    title="Документация API приложения VP Challenge",
    openapi_tags=tags_metadata,
    version="0.0.1"
)

# app.mount("/web", StaticFiles(directory="../files/static"), name="static")
app.mount("/img", StaticFiles(directory="../files/images"), name="images")

prefix_router = APIRouter(prefix="/api")

prefix_router.include_router(video_router)
prefix_router.include_router(user_router)
prefix_router.include_router(battle_router)
prefix_router.include_router(tag_router)
prefix_router.include_router(telegram_router)

app.include_router(prefix_router)

scheduler = AsyncIOScheduler()
scheduler.start()


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await init_system_tables()
    scheduler.add_job(check_battle_completion, trigger="interval", minutes=1)


@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()
