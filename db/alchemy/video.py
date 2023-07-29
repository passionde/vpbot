from typing import List

from sqlalchemy import desc, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from setting import VIDEOS_PER_PAGE
from db.models.video import Video
from db.alchemy.database import safe_commit


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


async def new_video(session: AsyncSession, video_id: str, user_id: int, tag_id: int) -> bool:
    """Создает новое видео"""
    # создание нового видео
    video = Video(
        video_id=video_id,
        user_id=user_id,
        tag_id=tag_id
    )
    session.add(video)
    return await safe_commit(session)


async def get_all_videos_by_tag(session: AsyncSession, tag_id: int, page: int) -> List[Video]:
    """Получение всех видео категории с учетом пагинации"""
    # Вычисление индекса первого видео на странице
    start_index = (abs(page) - 1) * VIDEOS_PER_PAGE

    # Запрос видео с заданным тэгом и пагинацией
    result = await session.execute(
        select(Video)
        .filter(and_(
            Video.tag_id == tag_id,
            Video.is_active == True
        ))
        .order_by(desc(Video.date_added))
        .offset(start_index)
        .limit(VIDEOS_PER_PAGE)
    )
    return list(result.scalars().all())


async def get_user_videos_by_tag(session: AsyncSession, tag_id: int, user_id: int) -> List[Video]:
    """Получение видео пользователя по категории"""
    result = await session.execute(
        select(Video)
        .filter(and_(
            Video.user_id == user_id,
            Video.tag_id == tag_id,
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
