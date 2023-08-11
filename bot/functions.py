import json
import os

from aiogram import types
from aiogram.utils.exceptions import BadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.vp_bot import vp_bot
from config import DOMAIN
from db.alchemy.battle import get_invitation, change_status_invitation, new_battle
from db.alchemy.video import get_video
from db.models.video import Video
from utils.youtube import get_video_info


async def check_and_get_videos(
        session: AsyncSession, user_id: int, user_video_id: str, opponent_video_id: str
) -> (Video, Video, str):
    """Проводит необходимые проверки, возвращает объекты видео и текст сообщения"""
    user_video = await get_video(session, user_video_id)
    if not user_video:
        return None, None, f"Видео пользователя не найдено [{user_video_id}]"
    if user_video.user_id != user_id:
        return None, None, f"Видео [{user_video_id}] принадлежит другому пользователю"

    opponent_video = await get_video(session, opponent_video_id)
    if not opponent_video:
        return None, None, f"Видео соперника не найдено [{opponent_video_id}]"

    return user_video, opponent_video, None


async def handle_refusal(callback: types.CallbackQuery, session: AsyncSession) -> (str, bool):
    """Отказаться от батла. Возвращает текст сообщения и логический результат"""
    invitation_id: int = dict(json.loads(callback.data)).get("invitation_id")
    if not invitation_id:
        return "Неверный формат данных", False

    invitation = await get_invitation(session, invitation_id)
    if not invitation:
        return f"Приглашение №{invitation_id} не найдено", False
    if invitation.status != "waiting":
        return f"По приглашению №{invitation_id} уже принято решение", False

    user_video, opponent_video, error = await check_and_get_videos(
        session,
        callback.message.chat.id,
        invitation.video_id_accepting,
        invitation.video_id_appointing
    )
    if error:
        return error, False

    result = await change_status_invitation(session, invitation.invitation_id, "cancel")  # todo сделать ENUM
    if not result:
        return "Произошла ошибка при сохранении в БД, попробуйте позже", False

    return "Вы отказались от вызова!", True


async def handle_agreement(callback: types.CallbackQuery, session: AsyncSession) -> (str, bool):
    """Согласиться на батл"""
    invitation_id: int = dict(json.loads(callback.data)).get("invitation_id")
    if not invitation_id:
        return "Неверный формат данных", False

    invitation = await get_invitation(session, invitation_id)
    if not invitation:
        return f"Приглашение №{invitation_id} не найдено", False
    if invitation.status != "waiting":
        return f"По приглашению №{invitation_id} уже принято решение", False

    user_video, opponent_video, error = await check_and_get_videos(
        session,
        callback.message.chat.id,
        invitation.video_id_accepting,
        invitation.video_id_appointing
    )
    if error:
        return error, False

    user_video_info = await get_video_info(user_video.video_id)
    if not user_video_info:
        return f"Не получилось найти видео пользователя [{user_video.video_id}]. Возможно оно удалено", False

    opponent_video_info = await get_video_info(opponent_video.video_id)
    if not opponent_video_info:
        return f"Не получилось найти видео соперника [{opponent_video.video_id}]. Возможно оно удалено", False

    result = await change_status_invitation(session, invitation.invitation_id, "agreement")  # todo сделать ENUM
    if not result:
        return "Произошла ошибка при сохранении в БД, попробуйте позже", False

    result = await new_battle(
        session,
        user_video.video_id, opponent_video.video_id,
        user_video_info.likes, opponent_video_info.likes,
        invitation_id, user_video.tag_name
    )
    if not result:
        return "Произошла ошибка при сохранении в БД, попробуйте позже", False

    return "Вы подтвердили участие в вызове!", True


async def get_profile_info(user_id: int):
    try:
        photo = await vp_bot.get_user_profile_photos(user_id, limit=1)
        user = (await vp_bot.get_chat_member(user_id, user_id)).user
    except BadRequest:
        return None

    img_path = f"../files/images/{user_id}.jpg"
    if not os.path.exists(img_path) and photo.photos:
        await photo.photos[0][0].download(destination_file=img_path)

    return {
        "photo_url_160": f"{DOMAIN}/img/{user_id}.jpg" if photo.photos else f"{DOMAIN}/img/no-img.png",
        "username_or_first_name": user.username if user.username else user.first_name,
        "url": user.url
    }
