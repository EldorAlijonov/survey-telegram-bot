from datetime import date, datetime, time

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        normalized = username.removeprefix("@").lower()
        result = await self.session.execute(select(User).where(func.lower(User.username) == normalized))
        return result.scalar_one_or_none()

    async def get_with_surveys(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.surveys)).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, username: str | None) -> User:
        user = User(telegram_id=telegram_id, username=username)
        self.session.add(user)
        await self.session.flush()
        return user

    async def delete_by_telegram_id(self, telegram_id: int) -> int:
        result = await self.session.execute(delete(User).where(User.telegram_id == telegram_id))
        return result.rowcount or 0

    async def count_all(self) -> int:
        return await self.session.scalar(select(func.count(User.id))) or 0

    async def count_registered_on(self, day: date) -> int:
        start = datetime.combine(day, time.min)
        end = datetime.combine(day, time.max)
        return await self.session.scalar(
            select(func.count(User.id)).where(User.created_at.between(start, end))
        ) or 0

    async def count_completed(self) -> int:
        return await self.session.scalar(
            select(func.count(User.id)).where(User.has_completed_survey.is_(True))
        ) or 0

    async def count_subscribed(self) -> int:
        return await self.session.scalar(
            select(func.count(User.id)).where(User.is_subscribed.is_(True))
        ) or 0

    async def list_by_date(self, day: date, limit: int, offset: int) -> list[User]:
        start = datetime.combine(day, time.min)
        end = datetime.combine(day, time.max)
        result = await self.session.execute(
            select(User)
            .where(User.created_at.between(start, end))
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_date(self, day: date) -> int:
        start = datetime.combine(day, time.min)
        end = datetime.combine(day, time.max)
        return await self.session.scalar(
            select(func.count(User.id)).where(User.created_at.between(start, end))
        ) or 0

    async def all_telegram_ids(self) -> list[int]:
        result = await self.session.execute(select(User.telegram_id).order_by(User.id))
        return list(result.scalars().all())

    async def list_for_export(self, day: date | None = None, completed_only: bool = False) -> list[User]:
        stmt = select(User).options(selectinload(User.surveys)).order_by(User.created_at.desc())
        if day is not None:
            stmt = stmt.where(User.created_at.between(datetime.combine(day, time.min), datetime.combine(day, time.max)))
        if completed_only:
            stmt = stmt.where(User.has_completed_survey.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())
