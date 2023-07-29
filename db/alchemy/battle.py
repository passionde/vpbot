from datetime import datetime, timedelta
from typing import List

from sqlalchemy import desc, or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from db.models.video import Video, Tag
from setting import BATTLE_DURATION_DAY, BATTLES_PER_PAGE
from db.models.battle import Participant, Battle, InvitationBattle
from db.alchemy.database import safe_commit


async def new_battle(session: AsyncSession, video_1: str, video_2: str, likes_1: int, likes_2: int) -> bool:
    # Создание объектов Participant
    participant_1 = Participant(number_likes_start=likes_1, number_likes_finish=likes_1, video_id=video_1)
    participant_2 = Participant(number_likes_start=likes_2, number_likes_finish=likes_2, video_id=video_2)
    session.add_all([participant_1, participant_2])
    await safe_commit(session)

    # Создание объекта Battle
    battle_start = datetime.now()
    battle_end = battle_start + timedelta(days=BATTLE_DURATION_DAY)
    battle = Battle(
        date_start=battle_start,
        date_end=battle_end,
        is_finish=False,
        participant_1=participant_1.participant_id,
        participant_2=participant_2.participant_id,
        winner=None
    )

    # Сохранение объектов в базе данных
    session.add(battle)
    return await safe_commit(session)


async def get_participant(session: AsyncSession, participant_id: int) -> Participant | None:
    """Получение участника батла по ID"""
    participant = await session.execute(
        select(Participant)
        .where(Participant.participant_id == participant_id)
    )
    participant = participant.first()
    if not participant:
        return None
    return participant[0]


async def get_user_battles(session: AsyncSession, user_id: int, page: int) -> List[Battle]:
    """Получение батлов пользователя"""
    # Вычисление индекса первого батла на странице
    start_index = (abs(page) - 1) * BATTLES_PER_PAGE

    # Запрос батлов, в которых пользователь участвовал с использованием пагинации
    query = (
        session.query(Battle)
        .filter(or_(Battle.participant_1 == user_id, Battle.participant_2 == user_id))
        .order_by(desc(Battle.date_start))
        .offset(start_index)
        .limit(BATTLES_PER_PAGE)
    )

    # Исполнение запроса и получение батлов
    result = await session.execute(query)
    return list(result.scalars().all())


# todo не используется, но возможно пригодится
async def get_all_current_battles(session: AsyncSession, page: int) -> List[Battle]:
    """Получение текущих незавершенных боев с учетом пагинации"""
    # Вычисление индекса первого батла на странице
    start_index = (abs(page) - 1) * BATTLES_PER_PAGE

    # Запрос незавершенных батлов с использованием пагинации
    result = await session.execute(
        select(Battle)
        .filter(Battle.is_finish != True)
        .order_by(desc(Battle.date_start))
        .offset(start_index)
        .limit(BATTLES_PER_PAGE)
    )
    # Исполнение запроса и получение батлов
    return list(result.scalars().all())


async def get_current_battles_by_tag(session: AsyncSession, page: int, tag_name: str) -> List[Battle]:
    """Получение текущих незавершенных боев с учетом пагинации и категории тэга"""
    start_index = (abs(page) - 1) * BATTLES_PER_PAGE

    # Создаем псевдонимы для таблицы Video и связанной таблицы Tag
    video_alias = aliased(Video)
    tag_alias = aliased(Tag)

    # Запрос незавершенных батлов с использованием пагинации и фильтрации по тэгу
    query = (
        select(Battle)
        .join(Participant, or_(
            Battle.participant_1 == Participant.participant_id,
            Battle.participant_2 == Participant.participant_id
        ))
        .join(video_alias, Participant.video_id == video_alias.video_id)
        .join(tag_alias, video_alias.tag_id == tag_alias.tag_id)
        .filter(Battle.is_finish != True, tag_alias.tag_name == tag_name)
        .order_by(desc(Battle.date_start))
        .offset(start_index)
        .limit(BATTLES_PER_PAGE)
        .distinct(Battle.battle_id)  # Исключение дупликатов боев по battle_id
    )

    # Выполняем запрос и получаем батлы
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_expired_battles(session: AsyncSession) -> List[Battle]:
    """Получение всех записей Battle, у которых время date_end меньше текущего времени."""
    current_time = datetime.now()

    # Выполняем запрос с фильтрацией по времени date_end
    expired_battles = await session.execute(
        select(Battle)
        .filter(and_(
            Battle.date_end < current_time,
            Battle.is_finish == False
        ))
    )

    return list(expired_battles.scalars().all())


async def add_invitation(session: AsyncSession, user_video_id: str, opponent_video_id: str) -> InvitationBattle:
    """Добавление нового приглашения на батл"""
    invitation = InvitationBattle(
        video_id_appointing=user_video_id,
        video_id_accepting=opponent_video_id
    )
    session.add(invitation)
    await safe_commit(session)
    return invitation


async def check_pending_prompts(session: AsyncSession, video_id_1: str, video_id_2: str) -> bool:
    """Проверяет наличие необработанных приглашений (status == 1). True - есть, False - нет"""
    invitation = await session.execute(
        select(InvitationBattle)
        .where(
            and_(
                or_(
                    InvitationBattle.video_id_accepting == video_id_1,
                    InvitationBattle.video_id_accepting == video_id_2
                ),
                or_(
                    InvitationBattle.video_id_appointing == video_id_1,
                    InvitationBattle.video_id_appointing == video_id_2
                ),
                InvitationBattle.status == 1
            )
        )
    )
    invitation = invitation.first()
    if invitation:
        return True
    return False


async def get_invitation(session: AsyncSession, invitation_id: int) -> InvitationBattle | None:
    """Получает приглашение по ID"""
    invitation = await session.execute(
        select(InvitationBattle)
        .where(InvitationBattle.invitation_id == invitation_id)
    )
    invitation = invitation.first()
    if not invitation:
        return None
    return invitation[0]


async def change_status_invitation(session: AsyncSession, invitation_id: int, status: int) -> bool:
    """Изменяет статус приглашения на батл\n
    1 - ожидание, 2 - отмена, 3 - согласие"""
    invitation = await get_invitation(session, invitation_id)
    if not invitation:
        return False

    invitation.status = status
    session.add(invitation)
    return await safe_commit(session)
