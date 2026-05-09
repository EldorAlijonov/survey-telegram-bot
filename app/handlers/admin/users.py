from datetime import date
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.keyboards.admin_inline import pagination_keyboard
from app.keyboards.admin_reply import date_select_keyboard
from app.services.user_service import UserService
from app.states.admin_states import AdminUsersStates
from app.utils.callbacks import safe_callback_answer
from app.utils.date_utils import format_dt, parse_uz_date, today, yesterday
from app.utils.pagination import clamp_page, pages_count

router = Router(name="admin_users")


@router.message(F.text.in_({"Bugun", "Kecha"}))
async def users_by_quick_date(message: Message, user_service: UserService, settings: Settings) -> None:
    day = today() if message.text == "Bugun" else yesterday()
    await send_users_page(message, user_service, settings, day, 0)


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
    await send_users_page(message, user_service, settings, day, 0)


@router.callback_query(F.data.startswith("users:"))
async def users_page_callback(callback: CallbackQuery, user_service: UserService, settings: Settings) -> None:
    _, day_raw, page_raw = callback.data.split(":")
    day = date.fromisoformat(day_raw)
    page = int(page_raw)
    if callback.message:
        text, keyboard = await build_users_page(user_service, settings, day, page)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_callback_answer(callback)


async def send_users_page(message: Message, user_service: UserService, settings: Settings, day: date, page: int) -> None:
    text, keyboard = await build_users_page(user_service, settings, day, page)
    await message.answer(text, reply_markup=keyboard or date_select_keyboard())


async def build_users_page(user_service: UserService, settings: Settings, day: date, page: int):
    total = await user_service.users.count_by_date(day)
    page = clamp_page(page, total, settings.page_size)
    users = await user_service.users.list_by_date(day, settings.page_size, page * settings.page_size)
    total_pages = pages_count(total, settings.page_size)
    rows = [f"👥 {day.strftime('%d.%m.%Y')} kuni ro'yxatdan o'tganlar: {total}\n"]
    if not users:
        rows.append("Bu sanada foydalanuvchilar topilmadi.")
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
    return "\n".join(rows), pagination_keyboard(f"users:{day.isoformat()}", page, total_pages)
