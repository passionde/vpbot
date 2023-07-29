from db.models.video import Tag
from db.alchemy.database import safe_commit
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.database import engine
from db.models.database import create_db_and_tables

# todo согласовать тэг по-умолчанию
tags = [
    "random",
    "vocal",
    "sport",
    "dance",
    "beatbox",
    "talent"
]


async def init_tags(session: AsyncSession):
    for tag_idx, tag in enumerate(tags, start=1):
        new_tag = Tag(
            tag_id=tag_idx,
            tag_name=tag
        )
        session.add(new_tag)


async def init_system_tables():
    await create_db_and_tables()
    async with engine.begin() as conn:
        async with AsyncSession(conn) as session:
            await init_tags(session)
            await safe_commit(session)
