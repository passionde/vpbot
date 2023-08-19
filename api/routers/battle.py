from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.exception import APIException
from api.dependencies.security import HeaderInitParams
from api.responses.battle import AppointBattleSchema, GetAllCurrentBattlesSchema, AssignRandomOpponentSchema
from api.schemas.base import SuccessResponse
from api.schemas.battle import BattleMethodRequest, GetAllCurrentBattlesRequest, AssignRandomOpponentRequest, \
    AssignRandomOpponentResponse, BattleInfoRequest, InvitationInfoRequest
from bot.functions import get_profile_info
from bot.notification import send_invitation_battle
from db.alchemy.battle import add_invitation, check_pending_prompts, get_current_battles_by_tag, assign_random_opponent, \
    get_invitation, get_battle
from db.alchemy.video import get_video
from db.models.database import get_async_session
from db.models.video import Video

router = APIRouter(prefix="/battle", tags=["Вызовы"])


async def check_and_get_videos(
        session: AsyncSession, user_id: int, user_video_id: str, opponent_video_id
) -> (Video, Video):
    """Проводит необходимые проверки и возвращает объекты видео"""
    user_video = await get_video(session, user_video_id)
    if not user_video or not user_video.is_active:
        raise APIException(1, f"user video not found ({user_video_id})")
    if user_video.user_id != user_id:
        raise APIException(3, f"video {user_video_id} belongs to another user")

    opponent_video = await get_video(session, opponent_video_id)
    if not opponent_video or not opponent_video.is_active:
        raise APIException(2, f"opponent video not found ({opponent_video_id})")

    return user_video, opponent_video


@router.post("/get-current-battles-by-tag", responses=GetAllCurrentBattlesSchema)
async def get_current_battles_by_tag_router(
        _: HeaderInitParams,
        params: GetAllCurrentBattlesRequest,
        session: AsyncSession = Depends(get_async_session)
):
    """Текущие батлы (незавершенные)"""
    current_battles = await get_current_battles_by_tag(session, params.page, params.tag)
    response = []
    for battle in current_battles:
        video_1 = await get_video(session, battle.video_id_1)
        video_2 = await get_video(session, battle.video_id_2)

        info_1 = await get_profile_info(video_1.user_id)
        if not info_1:
            continue

        info_2 = await get_profile_info(video_2.user_id)
        if not info_2:
            continue

        item = {
            "battle_id": battle.battle_id,
            "date_start": battle.date_start,
            "date_end": battle.date_end,
            "participant_1": {
                "video_id": battle.video_id_1,
                "likes_start": battle.likes_start_1,
                "user_id": video_1.user_id if video_1 else None,
                **info_1
            },
            "participant_2": {
                "video_id": battle.video_id_2,
                "likes_start": battle.likes_start_2,
                "user_id": video_2.user_id if video_2 else None,
                **info_2
            },
        }
        response.append(item)

    return {"items": response}


@router.post("/appoint-battle", responses=AppointBattleSchema)
async def appoint_battle_router(
        launch_params: HeaderInitParams,
        params: BattleMethodRequest,
        session: AsyncSession = Depends(get_async_session)
):
    """Назначить баттл"""
    user_video, opponent_video = await check_and_get_videos(
        session, launch_params.user_id, params.user_video_id, params.opponent_video_id
    )
    if user_video.tag_name != opponent_video.tag_name:
        raise APIException(5, "videos have different categories")

    exist = await check_pending_prompts(session, params.user_video_id, params.opponent_video_id)
    if exist:
        raise APIException(4, "this video has already been challenged")

    invitation = await add_invitation(session, params.user_video_id, params.opponent_video_id)

    await send_invitation_battle(user_video, opponent_video, invitation.invitation_id)
    return SuccessResponse(success=True)


@router.post("/assign-random-opponent", responses=AssignRandomOpponentSchema)
async def assign_random_opponent_router(
        launch_params: HeaderInitParams,
        params: AssignRandomOpponentRequest,
        session: AsyncSession = Depends(get_async_session)
):
    video_id = await assign_random_opponent(session, params.tag, launch_params.user_id)
    return AssignRandomOpponentResponse(
        video_id=video_id if video_id else ""
    )


@router.post("/get-battle-info")
async def get_battle_info_router(
        _: HeaderInitParams,
        params: BattleInfoRequest,
        session: AsyncSession = Depends(get_async_session)
):
    battle = await get_battle(session, params.battle_id)
    if not battle:
        raise APIException(1, "Battle not found")

    video_1 = await get_video(session, battle.video_id_1)
    video_2 = await get_video(session, battle.video_id_2)

    info_1 = await get_profile_info(video_1.user_id)
    if not info_1:
        raise APIException(2, "User 1 not found")

    info_2 = await get_profile_info(video_2.user_id)
    if not info_2:
        raise APIException(3, "User 2 not found")

    return {
        "battle_id": battle.battle_id,
        "date_start": battle.date_start,
        "date_end": battle.date_end,
        "participant_1": {
            "video_id": battle.video_id_1,
            "likes_start": battle.likes_start_1,
            "user_id": video_1.user_id if video_1 else None,
            **info_1
        },
        "participant_2": {
            "video_id": battle.video_id_2,
            "likes_start": battle.likes_start_2,
            "user_id": video_2.user_id if video_2 else None,
            **info_2
        },
    }


@router.post("/get-invitation-info")
async def get_invitation_info_router(
        _: HeaderInitParams,
        params: InvitationInfoRequest,
        session: AsyncSession = Depends(get_async_session)
):
    invitation = await get_invitation(session, params.invitation_id)
    if not invitation:
        raise APIException(1, "Invitation not found")

    video_1 = await get_video(session, invitation.video_id_appointing)
    video_2 = await get_video(session, invitation.video_id_accepting)

    info_1 = await get_profile_info(video_1.user_id)
    if not info_1:
        raise APIException(2, "User 1 not found")

    info_2 = await get_profile_info(video_2.user_id)
    if not info_2:
        raise APIException(3, "User 2 not found")

    return {
        "status": invitation.status,
        "date_create": invitation.date_added,
        "participant_1": {
            "video_id": invitation.video_id_appointing,
            "user_id": video_1.user_id if video_1 else None,
            **info_1
        },
        "participant_2": {
            "video_id": invitation.video_id_accepting,
            "user_id": video_2.user_id if video_2 else None,
            **info_2
        },
    }
