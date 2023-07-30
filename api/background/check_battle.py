from sqlalchemy.ext.asyncio import AsyncSession

from bot.notification import send_result_battle
from db.alchemy.battle import get_expired_battles, get_participant
from db.alchemy.user import change_vp_coins, change_rating
from db.alchemy.video import get_video
from db.models.battle import Battle, Participant
from db.models.database import async_session_maker
from setting import AWARD_FOR_VICTORY, DISCARD_FOR_LOSS, WIN_RANKING_CHANGE, LOSE_RANKING_CHANGE
from utils.youtube import get_video_info


videos_not_found: dict[int: int] = {}


def determine_winner(participant_1: Participant, participant_2: Participant) -> (int, int):
    """Определяет победителя и проигравшего. Возвращается ID победителя и ID проигравшего"""
    total_likes_1 = participant_1.number_likes_finish - participant_1.number_likes_finish
    total_likes_2 = participant_2.number_likes_finish - participant_2.number_likes_finish

    if total_likes_1 > total_likes_2:
        winner_id = participant_1.participant_id
    elif (total_likes_1 == total_likes_2) and participant_1.number_likes_start > participant_2.number_likes_start:
        winner_id = participant_1.participant_id
    else:
        winner_id = participant_2.participant_id

    if winner_id == participant_1.participant_id:
        loser_id = participant_2.participant_id
    else:
        loser_id = participant_1.participant_id

    return winner_id, loser_id


async def handle_battle(battle: Battle, session: AsyncSession):
    # Получение информации об участниках
    participant_1 = await get_participant(session, battle.participant_1)
    participant_2 = await get_participant(session, battle.participant_2)

    # Получение информации об видео
    video_1 = await get_video(session, participant_1.video_id)
    video_2 = await get_video(session, participant_2.video_id)

    info_1 = await get_video_info(participant_1.video_id)
    info_2 = await get_video_info(participant_2.video_id)

    # Подсчет лайков и определение победителя
    # Если нет ошибки, то записывается текущее число лайков
    # Если есть, то смотрится количество попыток, если их < 3 то завершается обработка
    # Если больше, то идет выполнение дальше и считается, что количество лайков не изменилось
    if info_1:
        participant_1.number_likes_finish = info_1.likes
    elif videos_not_found.get(participant_1.video_id, 0) + 1 < 3:
        videos_not_found[participant_1.video_id] = videos_not_found.get(participant_1.video_id, 0) + 1
        return

    if info_2:
        participant_2.number_likes_finish = info_2.likes
    elif videos_not_found.get(participant_2.video_id, 0) + 1 < 3:
        videos_not_found[participant_2.video_id] = videos_not_found.get(participant_2.video_id, 0) + 1
        return

    videos_not_found.pop(participant_1.video_id, None)
    videos_not_found.pop(participant_2.video_id, None)

    participant_winner_id, participant_looser_id = determine_winner(participant_1, participant_2)

    battle.winner = participant_winner_id
    battle.is_finish = True

    session.add_all((battle, participant_1, participant_2))
    await session.commit()

    if participant_winner_id == participant_1.participant_id:
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


async def check_battle_completion():
    async with async_session_maker() as session:
        expired_battles = await get_expired_battles(session)
        for battle in expired_battles:
            await handle_battle(battle, session)


