from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.models.admin import Admin
from app.repositories.admin_repository import AdminRepository
from app.repositories.user_repository import UserRepository
from app.utils.date_utils import format_dt


class AdminService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.admins = AdminRepository(session)
        self.users = UserRepository(session)

    async def is_admin(self, telegram_id: int) -> bool:
        if telegram_id in self.settings.main_admin_ids:
            return True
        return await self.admins.get_by_telegram_id(telegram_id) is not None

    async def is_main_admin(self, telegram_id: int) -> bool:
        if telegram_id in self.settings.main_admin_ids:
            return True
        admin = await self.admins.get_by_telegram_id(telegram_id)
        return bool(admin and admin.is_main)

    async def get_admin(self, telegram_id: int) -> Admin | None:
        return await self.admins.get_by_telegram_id(telegram_id)

    async def get_by_id(self, admin_id: int) -> Admin | None:
        return await self.admins.get(admin_id)

    async def add_admin(
        self,
        telegram_id: int,
        added_by: int,
        full_name: str | None = None,
        username: str | None = None,
        added_by_username: str | None = None,
    ) -> tuple[bool, str]:
        if await self.admins.get_by_telegram_id(telegram_id):
            return False, "⚠️ Bu foydalanuvchi allaqachon admin."
        admin = await self.admins.create(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username.removeprefix("@") if username else None,
            added_by=added_by,
            added_by_username=added_by_username,
            is_main=False,
        )
        await self.session.commit()
        return True, self.format_admin_added(admin)

    async def add_admin_by_username(
        self,
        username: str,
        added_by: int,
        added_by_username: str | None,
    ) -> tuple[bool, str]:
        user = await self.users.get_by_username(username)
        if user is None:
            return (
                False,
                "❌ Bu username orqali Telegram ID topilmadi.\n\n"
                "Foydalanuvchi botga avval /start bosgan bo'lishi kerak yoki Telegram ID yuboring.",
            )
        return await self.add_admin(
            telegram_id=user.telegram_id,
            full_name=user.full_name,
            username=user.username,
            added_by=added_by,
            added_by_username=added_by_username,
        )

    async def remove_admin(self, telegram_id: int) -> tuple[bool, str]:
        if telegram_id in self.settings.main_admin_ids:
            return False, "Asosiy adminni o'chirib bo'lmaydi."
        admin = await self.admins.get_by_telegram_id(telegram_id)
        if admin is None:
            return False, "Bunday admin topilmadi."
        await self.admins.delete(admin)
        await self.session.commit()
        return True, "Admin o'chirildi."

    async def remove_admin_by_id(self, admin_id: int, requested_by: int) -> tuple[bool, str]:
        if not await self.is_main_admin(requested_by):
            return False, "❌ Bu amal faqat asosiy adminlar uchun."
        admin = await self.admins.get(admin_id)
        if admin is None:
            return False, "Admin topilmadi."
        if admin.is_main or admin.telegram_id in self.settings.main_admin_ids:
            return False, "Asosiy adminni o'chirib bo'lmaydi."
        await self.admins.delete(admin)
        await self.session.commit()
        return True, "✅ Admin o'chirildi."

    async def list_admins(self, page: int, page_size: int) -> tuple[list[Admin], int]:
        total = await self.admins.count_all()
        admins = await self.admins.list_all(limit=page_size, offset=page * page_size)
        return admins, total

    def format_admin_card(self, admin: Admin) -> str:
        role = "Asosiy admin" if admin.is_main else "Oddiy admin"
        full_name = escape(admin.full_name or "Noma'lum")
        username = escape(f"@{admin.username}" if admin.username else "yo'q")
        added_by = escape(f"@{admin.added_by_username}" if admin.added_by_username else str(admin.added_by or "-"))
        return (
            f"👤 {full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 ID: {admin.telegram_id}\n"
            f"🛡 Turi: {role}\n"
            f"📅 Qo'shilgan sana: {format_dt(admin.created_at)}\n"
            f"➕ Qo'shgan admin: {added_by}"
        )

    def format_admin_added(self, admin: Admin) -> str:
        full_name = escape(admin.full_name or "Noma'lum")
        username = escape(f"@{admin.username}" if admin.username else "yo'q")
        return (
            "✅ Admin qo'shildi:\n"
            f"👤 Ism: {full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 Telegram ID: {admin.telegram_id}\n"
            f"📅 Sana: {format_dt(admin.created_at)}"
        )
