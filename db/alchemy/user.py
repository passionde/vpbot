from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import User
from db.alchemy.database import safe_commit


async def new_user(session: AsyncSession, user_id: int) -> User | None:
    user = User(user_id=user_id)
    session.add(user)

    if not await safe_commit(session):
        return None
    return user


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    user = await session.execute(
        select(User).where(User.user_id == user_id)
    )

    user = user.first()
    if not user:
        return None
    return user[0]


async def change_vp_coins(session: AsyncSession, user_id: int, term: int) -> bool:
    user = await get_user(session, user_id)
    if not user:
        return False

    new_vp_coins = user.vp_coins + term
    user.vp_coins = max(new_vp_coins, 0)

    return await safe_commit(session)


async def change_rating(session: AsyncSession, user_id: int, term: int) -> bool:
    user = await get_user(session, user_id)
    if not user:
        return False

    new_vp_rating = user.rating + term
    user.rating = max(new_vp_rating, 0)

    return await safe_commit(session)


async def get_all_users(session: AsyncSession) -> list[User]:
    users = await session.execute(
        select(User)
    )
    return list(users.scalars().all())