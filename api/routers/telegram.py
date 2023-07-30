from fastapi import APIRouter

from api.schemas.telegram import GetUserTgProfileRequest
from bot.functions import get_profile_info
from api.dependencies.security import HeaderInitParams

router = APIRouter(prefix="/user", tags=["Telegram"])


@router.post("/get-user-tg-profile")
async def get_user_videos_by_tag_router(
        _: HeaderInitParams,
        params: GetUserTgProfileRequest,
):
    # todo описать схемы
    return await get_profile_info(params.user_id)
