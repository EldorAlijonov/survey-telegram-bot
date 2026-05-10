from datetime import date
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.keyboards.admin_inline import user_delete_confirm_keyboard, users_list_keyboard
from app.keyboards.admin_reply import date_select_keyboard
from app.services.user_service import UserService
from app.states.admin_states import AdminUsersStates
from app.utils.callbacks import safe_callback_answer
from app.utils.date_utils import format_dt, parse_uz_date, today, yesterday
from app.utils.pagination import clamp_page, pages_count

router = Router(name="admin_users")

ALL_USERS_SCOPE = "all"


@router.message(F.text == "Barcha userlar")
async def users_all(message: Message, user_service: UserService, settings: Settings) -> None:
    await send_users_page(message, user_service, settings, ALL_USERS_SCOPE, 0)


@router.message(F.text.in_({"Bugun", "Kecha"}))
async def users_by_quick_date(message: Message, user_service: UserService, settings: Settings) -> None:
    day = today() if message.text == "Bugun" else yesterday()
    await send_users_page(message, user_service, settings, day.isoformat(), 0)


@router.message(F.text == "Sana kiritish")
async def users_custom_date(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminUsersStates.custom_date)
    await message.answer("Sanani kiriting. Format: 01.05.2026")


@router.message(AdminUsersStates.custom_date, F.text)
async def users_custom_date_finish(
    message: Message,
    state: FSMContext,
    user_service: UserService,
    settings: Settings,
) -> None:
    day = parse_uz_date(message.text)
    if day is None:
        await message.answer("Sana formati noto'g'ri. Masalan: 01.05.2026")
        return
    await state.clear()
    await send_users_page(message, user_service, settings, day.isoformat(), 0)


@router.callback_query(F.data.startswith("users:list:"))
async def users_page_callback(callback: CallbackQuery, user_service: UserService, settings: Settings) -> None:
    _, _, scope, page_raw = callback.data.split(":")
    page = int(page_raw)
    if callback.message:
        text, keyboard = await build_users_page(user_service, settings, scope, page)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("users:delete:"))
async def user_delete_prompt(callback: CallbackQuery, user_service: UserService) -> None:
    _, _, telegram_id_raw, scope, page_raw = callback.data.split(":")
    telegram_id = int(telegram_id_raw)
    user = await user_service.users.get_by_telegram_id(telegram_id)
    if user is None:
        await safe_callback_answer(callback, "Foydalanuvchi topilmadi.", show_alert=True)
        return
    username = escape("@" + user.username) if user.username else "-"
    full_name = escape(user.full_name or "-")
    if callback.message:
        await callback.message.edit_text(
            "Rostdan ham ushbu foydalanuvchini o'chirmoqchimisiz?\n\n"
            f"ID: {user.telegram_id}\n"
            f"Username: {username}\n"
            f"Ism familya: {full_name}",
            reply_markup=user_delete_confirm_keyboard(telegram_id, scope, int(page_raw)),
        )
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("users:delete_confirm:"))
async def user_delete_confirm(callback: CallbackQuery, user_service: UserService, settings: Settings) -> None:
    _, _, telegram_id_raw, scope, page_raw = callback.data.split(":")
    telegram_id = int(telegram_id_raw)
    page = int(page_raw)
    _, text = await user_service.delete_by_telegram_id(telegram_id)
    total = await count_users_by_scope(user_service, scope)
    page = clamp_page(page, total, settings.page_size)
    if callback.message:
        page_text, keyboard = await build_users_page(user_service, settings, scope, page)
        await callback.message.edit_text(page_text, reply_markup=keyboard or date_select_keyboard())
    await safe_callback_answer(callback, text, show_alert=True)


@router.callback_query(F.data.startswith("users:delete_cancel:"))
async def user_delete_cancel(callback: CallbackQuery, user_service: UserService, settings: Settings) -> None:
    _, _, scope, page_raw = callback.data.split(":")
    page = int(page_raw)
    if callback.message:
        text, keyboard = await build_users_page(user_service, settings, scope, page)
        await callback.message.edit_text(text, reply_markup=keyboard or date_select_keyboard())
    await safe_callback_answer(callback, "O'chirish bekor qilindi.")


async def send_users_page(message: Message, user_service: UserService, settings: Settings, scope: str, page: int) -> None:
    text, keyboard = await build_users_page(user_service, settings, scope, page)
    await message.answer(text, reply_markup=keyboard or date_select_keyboard())


async def build_users_page(user_service: UserService, settings: Settings, scope: str, page: int):
    total = await count_users_by_scope(user_service, scope)
    page = clamp_page(page, total, settings.page_size)
    users = await list_users_by_scope(user_service, scope, settings.page_size, page * settings.page_size)
    total_pages = pages_count(total, settings.page_size)
    rows = [users_page_title(scope, total)]
    if not users:
        rows.append("Foydalanuvchilar topilmadi.")
    for user in users:
        status = "Tugatgan" if user.has_completed_survey else "Tugatmagan"
        username = escape("@" + user.username) if user.username else "-"
        full_name = escape(user.full_name or "-")
        phone = escape(user.phone or "-")
        rows.append(
            f"ID: {user.telegram_id}\n"
            f"Username: {username}\n"
            f"Ism familya: {full_name}\n"
            f"Telefon: {phone}\n"
            f"So'rovnoma holati: {status}\n"
            f"Sana: {format_dt(user.created_at)}\n"
        )
    rows.append(f"Sahifa: {page + 1}/{total_pages}")
    return "\n".join(rows), users_list_keyboard([user.telegram_id for user in users], scope, page, total_pages)


async def count_users_by_scope(user_service: UserService, scope: str) -> int:
    if scope == ALL_USERS_SCOPE:
        return await user_service.users.count_all()
    return await user_service.users.count_by_date(date.fromisoformat(scope))


async def list_users_by_scope(user_service: UserService, scope: str, limit: int, offset: int):
    if scope == ALL_USERS_SCOPE:
        return await user_service.users.list_all(limit, offset)
    return await user_service.users.list_by_date(date.fromisoformat(scope), limit, offset)


def users_page_title(scope: str, total: int) -> str:
    if scope == ALL_USERS_SCOPE:
        return f"👥 Barcha foydalanuvchilar: {total}\n"
    day = date.fromisoformat(scope)
    return f"👥 {day.strftime('%d.%m.%Y')} kuni ro'yxatdan o'tganlar: {total}\n"
