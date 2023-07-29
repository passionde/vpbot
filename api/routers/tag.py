from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.database import get_async_session
from api.schemas.tags import TagInfo
from api.responses.tags import GetTagsSchema
from api.dependencies.security import HeaderInitParams
from db.alchemy.tag import get_tags

router = APIRouter(prefix="/user", tags=["Тэги"])


# todo Роутер для типов уведомлений
@router.post("/get-tags", responses=GetTagsSchema)
async def get_user_info_router(
        _: HeaderInitParams,
        session: AsyncSession = Depends(get_async_session)
):
    """Получение всех тэгов видео"""
    tags_categories = await get_tags(session)
    return TagInfo(
        tags_names=list(tags_categories.values())
    )
