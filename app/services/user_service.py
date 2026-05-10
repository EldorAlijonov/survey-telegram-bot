from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def get_or_create(self, tg_user: TelegramUser) -> User:
        user = await self.users.get_by_telegram_id(tg_user.id)
        if user is None:
            user = await self.users.create(telegram_id=tg_user.id, username=tg_user.username)
        else:
            user.username = tg_user.username
        await self.session.commit()
        return user

    async def update_profile(
        self,
        telegram_id: int,
        *,
        full_name: str | None = None,
        phone: str | None = None,
        mark_registered: bool = False,
    ) -> User:
        user = await self.users.get_by_telegram_id(telegram_id)
        if user is None:
            raise ValueError("User not found")
        if full_name is not None:
            user.full_name = full_name
        if phone is not None:
            user.phone = phone
        if mark_registered:
            user.is_registered = True
        await self.session.commit()
        return user

    async def get_profile_with_surveys(self, telegram_id: int) -> User | None:
        return await self.users.get_with_surveys(telegram_id)

    async def delete_by_telegram_id(self, telegram_id: int) -> tuple[bool, str]:
        user = await self.users.get_by_telegram_id(telegram_id)
        if user is None:
            return False, "Foydalanuvchi topilmadi."
        await self.users.delete_by_telegram_id(telegram_id)
        await self.session.commit()
        return True, "✅ Foydalanuvchi o'chirildi."

    async def mark_completed(self, telegram_id: int, subscribed: bool = True) -> User:
        user = await self.users.get_by_telegram_id(telegram_id)
        if user is None:
            raise ValueError("User not found")
        user.has_completed_survey = True
        user.is_subscribed = subscribed
        await self.session.commit()
        return user
