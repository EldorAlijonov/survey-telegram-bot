from aiogram import F, Router
from aiogram.types import Message

from app.services.stats_service import StatsService

router = Router(name="admin_statistics")


@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message, stats_service: StatsService) -> None:
    await message.answer(await stats_service.build_stats_text())
