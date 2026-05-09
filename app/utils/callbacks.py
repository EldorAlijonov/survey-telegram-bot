import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)

STALE_CALLBACK_MESSAGES = (
    "query is too old",
    "response timeout expired",
    "query ID is invalid",
)


async def safe_callback_answer(callback: CallbackQuery, *args, **kwargs) -> bool:
    try:
        await callback.answer(*args, **kwargs)
    except TelegramBadRequest as exc:
        message = str(exc)
        if any(part in message for part in STALE_CALLBACK_MESSAGES):
            logger.debug("Ignoring stale callback answer: %s", exc)
            return False
        raise
    return True
