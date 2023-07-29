from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.video import Tag

tags_info = {}


async def get_tags(session: AsyncSession) -> dict[int: str]:
    """Получение словаря тегов в формате {id: "Наименование"}"""
    global tags_info

    if tags_info:
        return tags_info

    tags = await session.execute(select(Tag.tag_id, Tag.tag_name))
    tags_info = {row[0]: row[1] for row in tags.fetchall()}
    return tags_info
