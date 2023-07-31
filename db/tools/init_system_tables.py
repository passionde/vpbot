from db.models.battle import StatusInvitation
from db.models.video import Tag
from db.alchemy.database import safe_commit
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.database import engine
from db.models.database import create_db_and_tables
from setting import TAGS_VIDEO

statuses = [
    "waiting",
    "cancel",
    "agreement",
    "completed"
]


async def init_tags(session: AsyncSession):
    for tag in TAGS_VIDEO:
        new_tag = Tag(
            tag=tag
        )
        session.add(new_tag)


async def init_status(session: AsyncSession):
    for status in statuses:
        new_tag = StatusInvitation(
            status=status
        )
        session.add(new_tag)


async def init_system_tables():
    await create_db_and_tables()
    async with engine.begin() as conn:
        async with AsyncSession(conn) as session:
            await init_tags(session)
            await init_status(session)
            await safe_commit(session)
