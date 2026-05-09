from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broadcast import Broadcast, BroadcastStatus


class BroadcastRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_draft(
        self,
        admin_id: int | None,
        admin_username: str | None,
        source_chat_id: int,
        source_message_id: int,
        source_message_ids: str | None,
        content_type: str | None,
        preview: str | None,
        reply_markup: str | None,
    ) -> Broadcast:
        broadcast = Broadcast(
            admin_id=admin_id,
            admin_username=admin_username,
            source_chat_id=source_chat_id,
            source_message_id=source_message_id,
            source_message_ids=source_message_ids,
            content_type=content_type,
            preview=preview,
            reply_markup=reply_markup,
            status=BroadcastStatus.draft,
        )
        self.session.add(broadcast)
        await self.session.flush()
        return broadcast

    async def get(self, broadcast_id: int) -> Broadcast | None:
        result = await self.session.execute(select(Broadcast).where(Broadcast.id == broadcast_id))
        return result.scalar_one_or_none()

    async def list_all(self, limit: int, offset: int) -> list[Broadcast]:
        result = await self.session.execute(
            select(Broadcast).order_by(Broadcast.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        return await self.session.scalar(select(func.count(Broadcast.id))) or 0

    async def delete(self, broadcast: Broadcast) -> None:
        await self.session.delete(broadcast)
