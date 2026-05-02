from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription


class SubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_active(self) -> list[Subscription]:
        result = await self.session.execute(
            select(Subscription)
            .where(Subscription.is_active == True)
            .order_by(Subscription.created_at.asc(), Subscription.id.asc())
        )
        return list(result.scalars().all())

    async def get_current(self) -> Subscription | None:
        active_result = await self.session.execute(
            select(Subscription)
            .where(Subscription.is_active.is_(True))
            .order_by(Subscription.created_at.desc(), Subscription.id.desc())
            .limit(1)
        )
        active = active_result.scalar_one_or_none()
        if active is not None:
            return active
        result = await self.session.execute(
            select(Subscription).order_by(Subscription.created_at.desc(), Subscription.id.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Subscription | None:
        result = await self.session.execute(select(Subscription).where(Subscription.channel_username == username))
        return result.scalar_one_or_none()

    async def get(self, subscription_id: int) -> Subscription | None:
        result = await self.session.execute(select(Subscription).where(Subscription.id == subscription_id))
        return result.scalar_one_or_none()

    async def list_all(self, limit: int, offset: int) -> list[Subscription]:
        result = await self.session.execute(
            select(Subscription).order_by(Subscription.created_at.desc(), Subscription.id.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        return await self.session.scalar(select(func.count(Subscription.id))) or 0

    async def create(self, title: str, username: str, url: str, chat_id: int | None) -> Subscription:
        subscription = Subscription(
            title=title,
            channel_username=username,
            channel_url=url,
            chat_id=chat_id,
            is_active=True,
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def delete(self, subscription: Subscription) -> None:
        await self.session.delete(subscription)
