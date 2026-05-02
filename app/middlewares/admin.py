from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.services.admin_service import AdminService


class AdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, admin_service: AdminService) -> bool:
        user = event.from_user
        return bool(user and await admin_service.is_admin(user.id))


class MainAdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, admin_service: AdminService) -> bool:
        user = event.from_user
        return bool(user and await admin_service.is_main_admin(user.id))


class NonAdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, admin_service: AdminService, **_: Any) -> bool:
        user = event.from_user
        return bool(user and not await admin_service.is_admin(user.id))
