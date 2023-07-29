from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.alchemy.tag import get_tags


async def get_tag_id(session: AsyncSession, tag_name) -> (int, dict[int: str]):
    """Возвращает ID тэга и словарь тэгов"""
    tag_id = None
    tags_categories = await get_tags(session)
    for t_id, t_name in tags_categories.items():
        if t_name == tag_name:
            tag_id = t_id
            break

    if not tag_id:
        raise HTTPException(
            status_code=400,
            detail={"error_code": 2, "msg": "tag not found"}
        )
    return tag_id, tags_categories
