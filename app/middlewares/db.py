from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.services.admin_service import AdminService
from app.services.broadcast_service import BroadcastService
from app.services.excel_service import ExcelService
from app.services.stats_service import StatsService
from app.services.subscription_service import SubscriptionService
from app.services.survey_service import SurveyService
from app.services.user_service import UserService


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker, settings: Settings) -> None:
        self.session_pool = session_pool
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            data["settings"] = self.settings
            data["user_service"] = UserService(session)
            data["admin_service"] = AdminService(session, self.settings)
            data["survey_service"] = SurveyService(session)
            data["subscription_service"] = SubscriptionService(session)
            data["broadcast_service"] = BroadcastService(session)
            data["excel_service"] = ExcelService(session)
            data["stats_service"] = StatsService(session)
            return await handler(event, data)
