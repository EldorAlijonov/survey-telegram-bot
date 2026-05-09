import asyncio
import json
import logging
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broadcast import Broadcast, BroadcastStatus
from app.repositories.broadcast_repository import BroadcastRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class BroadcastService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.broadcasts = BroadcastRepository(session)
        self.users = UserRepository(session)

    async def create_draft(
        self,
        admin_id: int | None,
        admin_username: str | None,
        chat_id: int,
        message_id: int,
        message_ids: list[int],
        content_type: str | None,
        preview: str | None,
        reply_markup: str | None,
    ) -> Broadcast:
        draft = await self.broadcasts.create_draft(
            admin_id=admin_id,
            admin_username=admin_username,
            source_chat_id=chat_id,
            source_message_id=message_id,
            source_message_ids=serialize_message_ids(message_ids),
            content_type=content_type,
            preview=preview,
            reply_markup=reply_markup,
        )
        await self.session.commit()
        return draft

    async def get(self, broadcast_id: int) -> Broadcast | None:
        return await self.broadcasts.get(broadcast_id)

    async def list_broadcasts(self, page: int, page_size: int) -> tuple[list[Broadcast], int]:
        total = await self.broadcasts.count_all()
        broadcasts = await self.broadcasts.list_all(limit=page_size, offset=page * page_size)
        return broadcasts, total

    async def update_source(
        self,
        broadcast_id: int,
        chat_id: int,
        message_id: int,
        message_ids: list[int],
        content_type: str | None,
        preview: str | None,
        reply_markup: str | None,
    ) -> tuple[bool, str]:
        broadcast = await self.broadcasts.get(broadcast_id)
        if broadcast is None:
            return False, "Reklama topilmadi."
        if broadcast.status == BroadcastStatus.running:
            return False, "❌ Yuborilayotgan reklamani tahrirlab bo'lmaydi."
        broadcast.source_chat_id = chat_id
        broadcast.source_message_id = message_id
        broadcast.source_message_ids = serialize_message_ids(message_ids)
        broadcast.content_type = content_type
        broadcast.preview = preview
        broadcast.reply_markup = reply_markup
        broadcast.status = BroadcastStatus.draft
        await self.session.commit()
        return True, "✅ Reklama yangilandi."

    async def delete(self, broadcast_id: int) -> tuple[bool, str]:
        broadcast = await self.broadcasts.get(broadcast_id)
        if broadcast is None:
            return False, "Reklama topilmadi."
        if broadcast.status == BroadcastStatus.running:
            return False, "❌ Yuborilayotgan reklamani o'chirib bo'lmaydi."
        await self.broadcasts.delete(broadcast)
        await self.session.commit()
        return True, "✅ Reklama o'chirildi."

    async def cancel(self, broadcast_id: int) -> Broadcast | None:
        broadcast = await self.broadcasts.get(broadcast_id)
        if broadcast:
            broadcast.status = BroadcastStatus.cancelled
            broadcast.finished_at = datetime.now()
            await self.session.commit()
        return broadcast

    async def send_to_all(self, bot: Bot, broadcast_id: int) -> Broadcast | None:
        broadcast = await self.broadcasts.get(broadcast_id)
        if broadcast is None:
            return None
        users = await self.users.all_telegram_ids()
        broadcast.total_users = len(users)
        broadcast.status = BroadcastStatus.running
        broadcast.started_at = datetime.now()
        broadcast.sent_count = 0
        broadcast.failed_count = 0
        await self.session.commit()

        for index, telegram_id in enumerate(users, start=1):
            try:
                message_ids = parse_message_ids(broadcast)
                if len(message_ids) == 1:
                    await bot.copy_message(
                        chat_id=telegram_id,
                        from_chat_id=broadcast.source_chat_id,
                        message_id=message_ids[0],
                        reply_markup=parse_reply_markup(broadcast.reply_markup),
                    )
                else:
                    await bot.copy_messages(
                        chat_id=telegram_id,
                        from_chat_id=broadcast.source_chat_id,
                        message_ids=message_ids,
                    )
                broadcast.sent_count += 1
            except TelegramAPIError as exc:
                broadcast.failed_count += 1
                logger.info("Broadcast %s failed for user %s: %s", broadcast.id, telegram_id, exc)
            await self.session.commit()
            if index % 25 == 0:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)

        broadcast.status = BroadcastStatus.finished
        broadcast.finished_at = datetime.now()
        await self.session.commit()
        return broadcast


def parse_reply_markup(value: str | None) -> InlineKeyboardMarkup | None:
    if not value:
        return None
    return InlineKeyboardMarkup.model_validate_json(value)


def serialize_message_ids(message_ids: list[int]) -> str | None:
    if len(message_ids) <= 1:
        return None
    return json.dumps(message_ids)


def parse_message_ids(broadcast: Broadcast) -> list[int]:
    if not broadcast.source_message_ids:
        return [broadcast.source_message_id]
    try:
        message_ids = json.loads(broadcast.source_message_ids)
    except json.JSONDecodeError:
        return [broadcast.source_message_id]
    if not isinstance(message_ids, list):
        return [broadcast.source_message_id]
    parsed = [message_id for message_id in message_ids if isinstance(message_id, int)]
    return parsed or [broadcast.source_message_id]
