from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.exception import APIException
from bot.functions import get_profile_info
from db.models.database import get_async_session
from api.schemas.user import GetUserInfoResponse
from api.responses.user import GetUserInfoSchema
from api.dependencies.security import HeaderInitParams
from db.alchemy.user import get_user

router = APIRouter(prefix="/user", tags=["Пользователи"])


@router.post("/get-user-info", responses=GetUserInfoSchema)
async def get_user_info_router(
        launch_params: HeaderInitParams,
        session: AsyncSession = Depends(get_async_session)
):
    """Данные профиля пользователя"""
    user = await get_user(session, launch_params.user_id)
    info = await get_profile_info(launch_params.user_id)

    if not info or not user:
        raise APIException(1, "Error when requesting telegram API")

    return GetUserInfoResponse(
        user_id=user.user_id,
        vp_coins=user.vp_coins,
        rating=user.rating,
        date_added=user.date_added,
        **info
    )
