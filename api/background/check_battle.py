from sqlalchemy.ext.asyncio import AsyncSession

from bot.notification import send_result_battle
from db.alchemy.battle import get_expired_battles, change_status_invitation
from db.alchemy.user import change_vp_coins, change_rating
from db.alchemy.video import get_video
from db.models.battle import Battle
from db.models.database import async_session_maker
from setting import AWARD_FOR_VICTORY, DISCARD_FOR_LOSS, WIN_RANKING_CHANGE, LOSE_RANKING_CHANGE
from utils.youtube import get_video_info


videos_not_found: dict[int: int] = {}


def determine_winner(battle: Battle) -> (int, int):
    """Определяет победителя и проигравшего. Возвращается ID  видио победителя и проигравшего"""
    total_likes_1 = battle.likes_finish_1 - battle.likes_start_1
    total_likes_2 = battle.likes_finish_2 - battle.likes_start_2

    if total_likes_1 > total_likes_2:
        winner_id, loser_id = battle.video_id_1, battle.video_id_2
    elif (total_likes_1 == total_likes_2) and battle.likes_start_1 > battle.likes_start_2:
        winner_id, loser_id = battle.video_id_1, battle.video_id_2
    else:
        winner_id, loser_id = battle.video_id_2, battle.video_id_1

    return winner_id, loser_id


async def handle_battle(battle: Battle, session: AsyncSession):
    # Получение информации об видео
    video_1 = await get_video(session, battle.video_id_1)
    video_2 = await get_video(session, battle.video_id_2)

    info_1 = await get_video_info(battle.video_id_1)
    info_2 = await get_video_info(battle.video_id_2)

    # Подсчет лайков и определение победителя
    # Если нет ошибки, то записывается текущее число лайков
    # Если есть, то смотрится количество попыток, если их < 3 то завершается обработка
    # Если больше, то идет выполнение дальше и считается, что количество лайков не изменилось
    if info_1:
        battle.likes_finish_1 = info_1.likes
    elif videos_not_found.get(battle.video_id_1, 0) + 1 < 3:
        videos_not_found[battle.video_id_1] = videos_not_found.get(battle.video_id_1, 0) + 1
        return

    if info_2:
        battle.likes_finish_2 = info_2.likes
    elif videos_not_found.get(battle.video_id_2, 0) + 1 < 3:
        videos_not_found[battle.video_id_2] = videos_not_found.get(battle.video_id_2, 0) + 1
        return

    videos_not_found.pop(battle.video_id_1, None)
    videos_not_found.pop(battle.video_id_2, None)

    video_winner_id, video_loser_id = determine_winner(battle)

    battle.winner_id = video_winner_id
    battle.loser_id = video_loser_id

    battle.is_finish = True
    session.add(battle)
    await session.commit()

    if video_winner_id == battle.video_id_1:
        user_winner_id, user_loser_id = video_1.user_id, video_2.user_id
    else:
        user_winner_id, user_loser_id = video_2.user_id, video_1.user_id

    # Отправка уведомления участникам
    await send_result_battle(user_winner_id, user_loser_id, battle.battle_id)

    # Изменение рейтинга и баланса участников
    await change_vp_coins(session, user_winner_id, AWARD_FOR_VICTORY)
    await change_vp_coins(session, user_loser_id, DISCARD_FOR_LOSS)

    await change_rating(session, user_winner_id, WIN_RANKING_CHANGE)
    await change_rating(session, user_loser_id, LOSE_RANKING_CHANGE)

    # todo сделать ENUM
    await change_status_invitation(session, battle.invitation_id, "completed")


async def check_battle_completion():
    async with async_session_maker() as session:
        expired_battles = await get_expired_battles(session)
        for battle in expired_battles:
            await handle_battle(battle, session)


