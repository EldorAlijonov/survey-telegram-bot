from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, MessageOriginUser

from app.config import Settings
from app.keyboards.admin_inline import admins_list_keyboard, confirm_keyboard
from app.keyboards.admin_reply import admin_manage_keyboard, cancel_admin_keyboard
from app.services.admin_service import AdminService
from app.states.admin_states import AdminManageStates
from app.utils.callbacks import safe_callback_answer
from app.utils.pagination import clamp_page, pages_count

router = Router(name="admin_admins")


@router.message(F.text == "➕ Admin qo'shish")
async def add_admin_start(message: Message, state: FSMContext, admin_service: AdminService) -> None:
    if not await admin_service.is_main_admin(message.from_user.id):
        await message.answer("❌ Bu amal faqat asosiy adminlar uchun.")
        return
    await state.set_state(AdminManageStates.add_admin)
    await message.answer(
        "Admin qilmoqchi bo'lgan foydalanuvchining xabarini shu yerga forward qiling.\n\n"
        "Muhim:\n"
        "- Foydalanuvchi botga avval /start bosgan bo'lishi kerak.\n"
        "- Agar forward orqali ID olinmasa, foydalanuvchi botga yozgan istalgan xabarni yuborsin yoki Telegram ID kiriting.",
        reply_markup=cancel_admin_keyboard(),
    )


@router.message(AdminManageStates.add_admin)
async def add_admin_finish(message: Message, state: FSMContext, admin_service: AdminService) -> None:
    if message.text == "❌ Bekor qilish":
        return

    added_by_username = message.from_user.username if message.from_user else None
    telegram_id, username, full_name = extract_admin_candidate(message)

    if telegram_id is None and username:
        ok, text = await admin_service.add_admin_by_username(
            username,
            added_by=message.from_user.id,
            added_by_username=added_by_username,
        )
    elif telegram_id is not None:
        ok, text = await admin_service.add_admin(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            added_by=message.from_user.id,
            added_by_username=added_by_username,
        )
    else:
        await message.answer("Telegram ID olinmadi. Forward qilingan xabar, Telegram ID yoki @username yuboring.")
        return

    await state.clear()
    await message.answer(text, reply_markup=admin_manage_keyboard())


def extract_admin_candidate(message: Message) -> tuple[int | None, str | None, str | None]:
    forward_from = getattr(message, "forward_from", None)
    if forward_from:
        return forward_from.id, forward_from.username, forward_from.full_name

    origin = getattr(message, "forward_origin", None)
    if isinstance(origin, MessageOriginUser):
        user = origin.sender_user
        return user.id, user.username, user.full_name

    text = (message.text or "").strip()
    if text.isdigit():
        return int(text), None, None
    if text.startswith("@") and len(text) > 1:
        return None, text.removeprefix("@"), None
    return None, None, None


@router.message(F.text == "📋 Adminlar ro'yxati")
async def list_admins(message: Message, admin_service: AdminService, settings: Settings) -> None:
    text, keyboard = await build_admins_page(admin_service, settings, 0)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("admins:list:"))
async def list_admins_callback(callback: CallbackQuery, admin_service: AdminService, settings: Settings) -> None:
    page = int(callback.data.split(":")[-1])
    if callback.message:
        text, keyboard = await build_admins_page(admin_service, settings, page)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("admin:delete:"))
async def admin_delete_prompt(callback: CallbackQuery, admin_service: AdminService) -> None:
    admin_id = int(callback.data.split(":")[-1])
    admin = await admin_service.get_by_id(admin_id)
    if admin is None:
        await safe_callback_answer(callback, "Admin topilmadi.", show_alert=True)
        return
    if admin.is_main:
        await safe_callback_answer(callback, "Asosiy adminni o'chirib bo'lmaydi.", show_alert=True)
        return
    if callback.message:
        await callback.message.answer(
            "Rostdan ham ushbu adminni o'chirmoqchimisiz?",
            reply_markup=confirm_keyboard(f"admin:delete_confirm:{admin_id}"),
        )
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("admin:delete_confirm:"))
async def admin_delete_confirm(callback: CallbackQuery, admin_service: AdminService) -> None:
    admin_id = int(callback.data.split(":")[-1])
    ok, text = await admin_service.remove_admin_by_id(admin_id, callback.from_user.id)
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text, reply_markup=admin_manage_keyboard())
    await safe_callback_answer(callback)


async def build_admins_page(admin_service: AdminService, settings: Settings, page: int):
    _, total = await admin_service.list_admins(0, settings.page_size)
    page = clamp_page(page, total, settings.page_size)
    admins, total = await admin_service.list_admins(page, settings.page_size)
    total_pages = pages_count(total, settings.page_size)
    rows = ["📋 Adminlar ro'yxati\n"]
    if not admins:
        rows.append("Adminlar topilmadi.")
    for index, admin in enumerate(admins, start=1):
        rows.append(f"{index}. {admin_service.format_admin_card(admin)}\n")
    rows.append(f"Sahifa: {page + 1}/{total_pages}")
    items = [(admin.id, not admin.is_main and admin.telegram_id not in settings.main_admin_ids) for admin in admins]
    return "\n".join(rows), admins_list_keyboard(items, page, total_pages)
