from typing import List

from sqlalchemy import desc, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.video import Video
from db.alchemy.database import safe_commit
from setting import ITEMS_PER_PAGE


async def change_is_active_status(session: AsyncSession, video: Video, is_active: bool) -> bool:
    """Меняет статус активности видео"""
    video.is_active = is_active
    session.add(video)
    return await safe_commit(session)


async def get_video(session: AsyncSession, video_id: str) -> Video | None:
    """Изменяет статус is_active, в случае отсутствия видео, возвращает False"""
    video = await session.execute(
        select(Video).where(Video.video_id == video_id)
    )
    video = video.first()
    if not video:
        return None

    return video[0]


async def new_video(session: AsyncSession, video_id: str, user_id: int, tag: str) -> bool:
    """Создает новое видео"""
    # создание нового видео
    video = Video(
        video_id=video_id,
        user_id=user_id,
        tag_name=tag
    )
    session.add(video)
    return await safe_commit(session)


async def get_videos_by_tag(session: AsyncSession, tag: str, page: int) -> List[Video]:
    """Получение всех видео категории с учетом пагинации"""
    # Вычисление индекса первого видео на странице
    start_index = (abs(page) - 1) * ITEMS_PER_PAGE

    # Запрос видео с заданным тэгом и пагинацией
    result = await session.execute(
        select(Video)
        .filter(and_(
            Video.tag_name == tag,
            Video.is_active == True
        ))
        .order_by(desc(Video.date_added))
        .offset(start_index)
        .limit(ITEMS_PER_PAGE)
    )
    return list(result.scalars().all())


async def get_user_videos_by_tag(session: AsyncSession, tag: str, user_id: int) -> List[Video]:
    """Получение видео пользователя по категории"""
    result = await session.execute(
        select(Video)
        .filter(and_(
            Video.user_id == user_id,
            Video.tag_name == tag,
            Video.is_active == True
        ))
    )
    return list(result.scalars().all())


async def get_user_all_videos(session: AsyncSession, user_id: int) -> List[Video]:
    """Получение всех клипов пользователя"""
    result = await session.execute(
        select(Video)
        .filter(and_(
            Video.user_id == user_id,
            Video.is_active == True
        ))
    )
    return list(result.scalars().all())
