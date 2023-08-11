from fastapi import APIRouter
from api.schemas.tags import TagInfo
from api.responses.tags import GetTagsSchema
from api.dependencies.security import HeaderInitParams
from setting import TAGS_VIDEO

router = APIRouter(prefix="/tags", tags=["Тэги"])


@router.post("/get-tags", responses=GetTagsSchema)
async def get_user_info_router(_: HeaderInitParams):
    """Получение всех тэгов видео"""
    return TagInfo(
        tags_names=TAGS_VIDEO
    )
