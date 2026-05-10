from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.admin_reply import (
    admin_manage_keyboard,
    admin_panel_keyboard,
    broadcast_menu_keyboard,
    date_select_keyboard,
    export_keyboard,
    subscription_manage_keyboard,
)
from app.utils.callbacks import safe_callback_answer

router = Router(name="admin_panel")


@router.message(F.text.in_({"🏠 Admin panel", "⬅️ Ortga"}))
async def show_admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Admin panel.", reply_markup=admin_panel_keyboard())


@router.message(F.text == "❌ Bekor qilish")
async def cancel_admin_action(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_panel_keyboard())


@router.callback_query((F.data == "cancel") | (F.data.endswith(":cancel")))
async def cancel_admin_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Amal bekor qilindi.", reply_markup=admin_panel_keyboard())
    await safe_callback_answer(callback)


@router.message(F.text == "👤 Adminlar")
async def admin_manage_menu(message: Message) -> None:
    await message.answer("Adminlar bo'limi.", reply_markup=admin_manage_keyboard())


@router.message(F.text == "📢 Majburiy obunalar")
async def subscription_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Majburiy obunalar bo'limi.", reply_markup=subscription_manage_keyboard())


@router.message(F.text == "📣 Reklama")
async def broadcast_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Reklama bo'limi.", reply_markup=broadcast_menu_keyboard())


@router.message(F.text == "👥 Foydalanuvchilar")
async def users_menu(message: Message) -> None:
    await message.answer("Foydalanuvchilarni ko'rish turini tanlang.", reply_markup=date_select_keyboard())


@router.message(F.text == "📥 Excel yuklab olish")
async def export_menu(message: Message) -> None:
    await message.answer("Excel eksport turini tanlang.", reply_markup=export_keyboard())
