import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError

from app.config import get_settings
from app.database.init import sync_main_admins
from app.database.session import async_session_maker, engine
from app.handlers.admin import get_admin_router
from app.handlers.user import get_user_router
from app.logging_config import setup_logging
from app.middlewares.db import DbSessionMiddleware

logger = logging.getLogger(__name__)


async def delete_webhook_with_retry(bot: Bot, attempts: int = 3) -> None:
    for attempt in range(1, attempts + 1):
        try:
            await bot.delete_webhook(drop_pending_updates=True, request_timeout=60)
            return
        except TelegramNetworkError as exc:
            if attempt == attempts:
                logger.exception("Could not delete Telegram webhook after %s attempts.", attempts)
                raise
            delay = attempt * 5
            logger.warning(
                "Telegram webhook delete timed out, retrying in %s seconds (%s/%s): %s",
                delay,
                attempt,
                attempts,
                exc,
            )
            await asyncio.sleep(delay)


async def notify_main_admins(bot: Bot, text: str) -> None:
    settings = get_settings()
    for admin_id in settings.main_admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except TelegramAPIError as exc:
            logger.warning("Startup notification was not sent to admin %s: %s", admin_id, exc)


async def on_startup(bot: Bot) -> None:
    settings = get_settings()
    try:
        async with async_session_maker() as session:
            await sync_main_admins(session, settings)
    except Exception:
        logger.exception("Bot startup failed. Check DATABASE_URL and PostgreSQL credentials.")
        await notify_main_admins(
            bot,
            "❌ Bot ishga tushmadi.\n\n"
            "PostgreSQL bazasiga ulanishda xatolik bor. DATABASE_URL login/parol va database nomini tekshiring.",
        )
        raise

    message = "✅ Bot muvaffaqiyatli ishga tushdi."
    logger.info(message)
    print(message)
    await notify_main_admins(bot, message)


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.update.middleware(DbSessionMiddleware(async_session_maker, settings))
    dp.include_router(get_admin_router())
    dp.include_router(get_user_router())

    try:
        await delete_webhook_with_retry(bot)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
