from aiogram.types import User
from sqlalchemy.ext.asyncio import AsyncSession

from bot.vp_bot import vp_bot
from bot.keyboard import battle_keyboard_for_user, battle_keyboard_for_opponent
from db.alchemy.battle import get_invitation
from db.alchemy.video import get_video
from db.models.video import Video
from setting import AWARD_FOR_VICTORY, DISCARD_FOR_LOSS


def get_username(user: User) -> str:
    name = "Unknown"
    if user.username:
        name = user.username
    elif user.first_name:
        name = user.first_name

    return name


async def send_invitation_battle(user_video: Video, opponent_video: Video, invitation_id: int):
    user = (await vp_bot.get_chat_member(user_video.user_id, user_video.user_id)).user
    opponent = (await vp_bot.get_chat_member(opponent_video.user_id, opponent_video.user_id)).user

    await vp_bot.send_message(
        user_video.user_id,
        f"Вы бросили вызов <a href=\"tg://user?id={opponent.id}\">{get_username(opponent)}</a>!",
        reply_markup=battle_keyboard_for_user(invitation_id),
        parse_mode="HTML"
    )

    await vp_bot.send_message(
        opponent_video.user_id,
        f"<a href=\"tg://user?id={user.id}\">{get_username(user)}</a> бросил вам вызов!",
        reply_markup=battle_keyboard_for_opponent(invitation_id),
        parse_mode="HTML"
    )


async def send_refuse_battle(invitation_id: int, session: AsyncSession):
    invitation = await get_invitation(session, invitation_id)

    user_video = await get_video(session, invitation.video_id_appointing)
    opponent_video = await get_video(session, invitation.video_id_accepting)

    opponent = (await vp_bot.get_chat_member(opponent_video.user_id, opponent_video.user_id)).user

    await vp_bot.send_message(
        user_video.user_id,
        f"<a href=\"tg://user?id={opponent.id}\">{get_username(opponent)}</a> отказался от вызова",
        reply_markup=battle_keyboard_for_user(invitation_id),
        parse_mode="HTML"
    )


async def send_agreement_battle(invitation_id: int, session: AsyncSession):
    invitation = await get_invitation(session, invitation_id)

    user_video = await get_video(session, invitation.video_id_appointing)
    opponent_video = await get_video(session, invitation.video_id_accepting)

    opponent = (await vp_bot.get_chat_member(opponent_video.user_id, opponent_video.user_id)).user

    await vp_bot.send_message(
        user_video.user_id,
        f"<a href=\"tg://user?id={opponent.id}\">{opponent.username if opponent.username else opponent.first_name}</a> подтвердил участие в вызове",
        reply_markup=battle_keyboard_for_user(invitation_id),
        parse_mode="HTML"
    )


async def send_result_battle(winner_id: int, loser_id: int, battle_id: int):
    # todo сделать кнопку просмотра результатов
    await vp_bot.send_message(
        winner_id,
        f"Ура, ты победил! Тебе начислены +{AWARD_FOR_VICTORY} VPcoins!",
        reply_markup=battle_keyboard_for_user(battle_id, is_invitation=False)
    )
    await vp_bot.send_message(
        loser_id,
        f"Поражение... {DISCARD_FOR_LOSS} VPcoins. Не расстраивайся!",
        reply_markup=battle_keyboard_for_user(battle_id, is_invitation=False)
    )
