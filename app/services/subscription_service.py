import logging
import re
from html import escape
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository

logger = logging.getLogger(__name__)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{5,32}$")


class SubscriptionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.subscriptions = SubscriptionRepository(session)

    def normalize_username(self, value: str) -> str | None:
        username = value.strip()
        if username.startswith("https://t.me/"):
            username = username.removeprefix("https://t.me/")
        elif username.startswith("http://t.me/"):
            username = username.removeprefix("http://t.me/")
        elif username.startswith("t.me/"):
            username = username.removeprefix("t.me/")
        if username.startswith("@"):
            username = username[1:]
        username = username.strip().strip("/")
        if "/" in username or not USERNAME_RE.fullmatch(username):
            return None
        return username.lower()

    async def validate_public_channel(self, bot: Bot, username: str) -> tuple[bool, str, Any | None]:
        try:
            chat = await bot.get_chat(f"@{username}")
        except TelegramBadRequest:
            return False, "❌ Kanal topilmadi yoki havola noto'g'ri.", None
        except TelegramForbiddenError:
            return (
                False,
                "❌ Bot ushbu kanalga kira olmayapti yoki kanalda admin emas.\n\n"
                "Iltimos, botni kanalga admin qilib qo'shing.",
                None,
            )

        if chat.type != "channel" or not chat.username:
            return False, "❌ Faqat ommaviy kanal qo'shish mumkin.", None

        try:
            member = await bot.get_chat_member(chat.id, bot.id)
        except TelegramForbiddenError:
            return (
                False,
                "❌ Bot ushbu kanalga kira olmayapti yoki kanalda admin emas.\n\n"
                "Iltimos, botni kanalga admin qilib qo'shing.",
                None,
            )
        except TelegramBadRequest:
            return False, "❌ Kanal topilmadi yoki havola noto'g'ri.", None

        if member.status not in {"administrator", "creator"}:
            return (
                False,
                "❌ Bot ushbu kanalda admin emas.\n\n"
                "Iltimos, avval botni kanalga admin qiling, keyin qayta urinib ko'ring.",
                None,
            )
        return True, "Kanal tekshiruvdan o'tdi.", chat

    async def add_channel(self, bot: Bot, raw_username: str) -> tuple[bool, str]:
        username = self.normalize_username(raw_username)
        if username is None:
            return False, "❌ Kanal topilmadi. Havola yoki username to'g'ri ekanini tekshiring."
        if await self.subscriptions.get_by_username(username):
            return False, "⚠️ Bu kanal allaqachon majburiy obunaga qo'shilgan."
        ok, message, chat = await self.validate_public_channel(bot, username)
        if not ok:
            return False, message
        title = chat.title or username
        await self.subscriptions.create(title=title, username=username, url=f"https://t.me/{username}", chat_id=chat.id)
        await self.session.commit()
        safe_title = escape(title)
        safe_username = escape(username)
        return True, (
            "✅ Majburiy obuna kanali qo'shildi:\n"
            f"📢 Kanal: {safe_title}\n"
            f"🔗 Havola: https://t.me/{safe_username}"
        )

    async def edit_channel(self, bot: Bot, raw_username: str) -> tuple[bool, str]:
        subscription = await self.subscriptions.get_current()
        if subscription is None:
            return False, "Hozircha kanal qo'shilmagan."
        username = self.normalize_username(raw_username)
        if username is None:
            return False, "❌ Kanal topilmadi. Havola yoki username to'g'ri ekanini tekshiring."
        existing = await self.subscriptions.get_by_username(username)
        if existing and existing.id != subscription.id:
            return False, "⚠️ Bu kanal allaqachon majburiy obunaga qo'shilgan."
        ok, message, chat = await self.validate_public_channel(bot, username)
        if not ok:
            return False, message
        title = chat.title or username
        subscription.title = title
        subscription.channel_username = username
        subscription.channel_url = f"https://t.me/{username}"
        subscription.chat_id = chat.id
        await self.session.commit()
        safe_title = escape(title)
        safe_username = escape(username)
        return True, (
            "✅ Majburiy obuna kanali yangilandi:\n"
            f"📢 Kanal: {safe_title}\n"
            f"🔗 Havola: https://t.me/{safe_username}"
        )

    async def delete_current(self) -> tuple[bool, str]:
        subscription = await self.subscriptions.get_current()
        if subscription is None:
            return False, "O'chirish uchun kanal topilmadi."
        await self.subscriptions.delete(subscription)
        await self.session.commit()
        return True, "Kanal o'chirildi."

    async def delete_by_id(self, subscription_id: int) -> tuple[bool, str]:
        subscription = await self.subscriptions.get(subscription_id)
        if subscription is None:
            return False, "Kanal topilmadi."
        await self.subscriptions.delete(subscription)
        await self.session.commit()
        return True, "✅ Kanal majburiy obunadan o'chirildi."

    async def toggle_by_id(self, subscription_id: int) -> tuple[bool, str]:
        subscription = await self.subscriptions.get(subscription_id)
        if subscription is None:
            return False, "Kanal topilmadi."
        subscription.is_active = not subscription.is_active
        await self.session.commit()
        return True, "Kanal holati yangilandi."

    async def edit_by_id(self, bot: Bot, subscription_id: int, raw_username: str) -> tuple[bool, str]:
        subscription = await self.subscriptions.get(subscription_id)
        if subscription is None:
            return False, "Kanal topilmadi."
        username = self.normalize_username(raw_username)
        if username is None:
            return False, "❌ Kanal topilmadi. Havola yoki username to'g'ri ekanini tekshiring."
        existing = await self.subscriptions.get_by_username(username)
        if existing and existing.id != subscription.id:
            return False, "⚠️ Bu kanal allaqachon majburiy obunaga qo'shilgan."
        ok, message, chat = await self.validate_public_channel(bot, username)
        if not ok:
            return False, message
        title = chat.title or username
        subscription.title = title
        subscription.channel_username = username
        subscription.channel_url = f"https://t.me/{username}"
        subscription.chat_id = chat.id
        await self.session.commit()
        safe_title = escape(title)
        safe_username = escape(username)
        return True, (
            "✅ Majburiy obuna kanali yangilandi:\n"
            f"📢 Kanal: {safe_title}\n"
            f"🔗 Havola: https://t.me/{safe_username}"
        )

    async def set_active(self, is_active: bool) -> tuple[bool, str]:
        subscription = await self.subscriptions.get_current()
        if subscription is None:
            return False, "Avval kanal qo'shing."
        subscription.is_active = is_active
        await self.session.commit()
        return True, "Majburiy obuna aktiv qilindi." if is_active else "Majburiy obuna noaktiv qilindi."

    async def get_all_active(self) -> list[Subscription]:
        return await self.subscriptions.get_all_active()

    async def get_current_channel(self) -> Subscription | None:
        return await self.subscriptions.get_current()

    async def get_channel(self, subscription_id: int) -> Subscription | None:
        return await self.subscriptions.get(subscription_id)

    async def page_for_channel(self, subscription_id: int, page_size: int) -> int:
        total = await self.subscriptions.count_all()
        if total == 0:
            return 0
        channels = await self.subscriptions.list_all(limit=total, offset=0)
        for index, channel in enumerate(channels):
            if channel.id == subscription_id:
                return index // page_size
        return 0

    async def list_channels(self, page: int, page_size: int) -> tuple[list[Subscription], int]:
        total = await self.subscriptions.count_all()
        channels = await self.subscriptions.list_all(limit=page_size, offset=page * page_size)
        return channels, total

    async def is_subscribed(self, bot: Bot, user_id: int, subscription: Subscription) -> bool:
        chat_id: int | str = subscription.chat_id or f"@{subscription.channel_username}"
        return await self.check_user(bot, user_id, chat_id)

    async def check_user(self, bot: Bot, user_id: int, chat_id: int | str) -> bool:
        try:
            member = await bot.get_chat_member(chat_id, user_id)
        except (TelegramBadRequest, TelegramForbiddenError) as exc:
            logger.warning("Subscription check failed: %s", exc)
            return False
        except Exception:
            logger.exception("Unexpected subscription check error")
            return False
        return member.status in {"member", "administrator", "creator"}
