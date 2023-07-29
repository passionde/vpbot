from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession


async def safe_commit(session: AsyncSession) -> bool:
    try:
        await session.commit()
    except DatabaseError:
        await session.rollback()
        return False

    return True
