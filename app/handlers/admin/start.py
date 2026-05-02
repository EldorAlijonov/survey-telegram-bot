from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.admin_reply import admin_panel_keyboard

router = Router(name="admin_start")


@router.message(CommandStart())
async def admin_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    name = message.from_user.full_name if message.from_user else "admin"
    await message.answer(
        f"Assalomu alaykum, {name}, xush kelibsiz. Siz ushbu botda adminsiz.",
        reply_markup=admin_panel_keyboard(),
    )
