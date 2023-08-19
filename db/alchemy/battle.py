import random
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import desc, or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.alchemy.video import get_user_videos_by_tag
from db.models.video import Video
from setting import ITEMS_PER_PAGE, BATTLE_DURATION_HOUR
from db.models.battle import Battle, InvitationBattle
from db.alchemy.database import safe_commit


async def new_battle(
        session: AsyncSession, video_1: str, video_2: str, likes_1: int, likes_2: int,
        invitation_id: int, tag: str
) -> bool:
    battle_start = datetime.now()
    battle_end = battle_start + timedelta(hours=BATTLE_DURATION_HOUR)

    battle = Battle(
        date_start=battle_start,
        date_end=battle_end,
        video_id_1=video_1,
        video_id_2=video_2,
        likes_start_1=likes_1,
        likes_start_2=likes_2,
        likes_finish_1=likes_1,
        likes_finish_2=likes_2,
        invitation_id=invitation_id,
        tag_name=tag
    )
    session.add(battle)
    return await safe_commit(session)


async def get_battle(session: AsyncSession, battle_id: int) -> Battle | None:
    """Получает батл по ID"""
    battle = await session.execute(
        select(Battle)
        .where(Battle.battle_id == battle_id)
    )
    battle = battle.first()
    if not battle:
        return None
    return battle[0]


async def get_current_battles_by_tag(session: AsyncSession, page: int, tag: str) -> List[Battle]:
    """Получение текущих незавершенных боев с учетом пагинации и категории тэга"""
    start_index = (abs(page) - 1) * ITEMS_PER_PAGE

    # Запрос незавершенных батлов с использованием пагинации и фильтрации по тэгу
    result = await session.execute(
        select(Battle)
        .filter(and_(
            Battle.is_finish == False,
            Battle.tag_name == tag
        ))
        .order_by(desc(Battle.date_start))
        .offset(start_index)
        .limit(ITEMS_PER_PAGE)
    )
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
    """Проверяет наличие необработанных приглашений (status == waiting). True - есть, False - нет"""
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
                or_(
                    InvitationBattle.status == "waiting",  # todo сделать ENUM
                    InvitationBattle.status == "agreement"  # todo сделать ENUM
                )

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


async def change_status_invitation(session: AsyncSession, invitation_id: int, status: str) -> bool:
    """Изменяет статус приглашения на батл"""
    invitation = await get_invitation(session, invitation_id)
    if not invitation:
        return False

    invitation.status = status
    session.add(invitation)
    return await safe_commit(session)


async def get_user_ignore_set(session: AsyncSession, user_videos: list[Video]) -> set[str]:
    user_id_videos = {video.video_id for video in user_videos}

    result = await session.execute(
        select(InvitationBattle)
        .where(and_(
            or_(
                InvitationBattle.video_id_accepting.in_(user_id_videos),
                InvitationBattle.video_id_appointing.in_(user_id_videos)

            ),
            InvitationBattle.status.in_(("waiting", "agreement"))
        ))
    )

    ignore_set_video_id = set()
    for invitation in list(result.scalars().all()):
        ignore_set_video_id.add(invitation.video_id_appointing)
        ignore_set_video_id.add(invitation.video_id_accepting)

    return ignore_set_video_id


async def assign_random_opponent(session: AsyncSession, tag: str, user_id: int) -> str | None:
    """Возвращает ID видео из категории tag, не принадлежащее пользователю с user_id"""

    # Возможные претенденты
    set_video_id = await session.execute(
        select(Video.video_id)
        .where(and_(
            Video.user_id != user_id,
            Video.tag_name == tag,
            Video.is_active == True
        ))
    )
    set_video_id = set(set_video_id.scalars().all())

    user_videos = await get_user_videos_by_tag(session, tag, user_id)

    # Множество видео для пропуска
    ignore_set_video_id = await get_user_ignore_set(session, user_videos)

    set_video_id = set_video_id - ignore_set_video_id
    return random.choice(list(set_video_id)) if set_video_id else None
