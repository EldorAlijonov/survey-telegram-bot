from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.keyboards.admin_inline import (
    broadcast_actions_keyboard,
    broadcast_list_keyboard,
    confirm_keyboard,
    send_confirm_keyboard,
)
from app.keyboards.admin_reply import broadcast_menu_keyboard, cancel_admin_keyboard
from app.models.broadcast import Broadcast, BroadcastStatus
from app.services.admin_service import AdminService
from app.services.broadcast_service import BroadcastService
from app.states.broadcast_states import BroadcastStates
from app.utils.date_utils import format_dt
from app.utils.pagination import clamp_page, pages_count

router = Router(name="admin_broadcast")


@router.message(F.text == "➕ Reklama yaratish")
async def create_broadcast_start(message: Message, state: FSMContext) -> None:
    await state.set_state(BroadcastStates.waiting_post)
    await message.answer(
        "Reklama postini yuboring. Post matn, rasm, video, animation, document yoki captionli media bo'lishi mumkin.",
        reply_markup=cancel_admin_keyboard(),
    )


@router.message(F.text.in_({"✏️ Reklamani tahrirlash", "🗑 Reklamani o'chirish", "🚀 Reklama yuborish"}))
async def broadcast_action_hint(message: Message) -> None:
    await message.answer("Amalni ro'yxatdan tanlang.", reply_markup=broadcast_menu_keyboard())


@router.message(BroadcastStates.waiting_post)
async def receive_broadcast_post(
    message: Message,
    state: FSMContext,
    admin_service: AdminService,
    broadcast_service: BroadcastService,
) -> None:
    if message.text == "❌ Bekor qilish":
        return
    admin = await admin_service.get_admin(message.from_user.id)
    content_type, preview = extract_broadcast_preview(message)
    draft = await broadcast_service.create_draft(
        admin_id=admin.id if admin else None,
        admin_username=message.from_user.username if message.from_user else None,
        chat_id=message.chat.id,
        message_id=message.message_id,
        content_type=content_type,
        preview=preview,
    )
    await state.clear()
    await message.answer("✅ Reklama saqlandi.", reply_markup=broadcast_menu_keyboard())
    await message.answer(
        format_broadcast_card(draft),
        reply_markup=broadcast_actions_keyboard(draft.id, include_list=True),
    )


@router.message(BroadcastStates.editing_post)
async def receive_broadcast_edit(
    message: Message,
    state: FSMContext,
    broadcast_service: BroadcastService,
) -> None:
    if message.text == "❌ Bekor qilish":
        return
    data = await state.get_data()
    broadcast_id = int(data["broadcast_id"])
    content_type, preview = extract_broadcast_preview(message)
    ok, text = await broadcast_service.update_source(
        broadcast_id,
        chat_id=message.chat.id,
        message_id=message.message_id,
        content_type=content_type,
        preview=preview,
    )
    await state.clear()
    await message.answer(text, reply_markup=broadcast_menu_keyboard())


@router.message(F.text == "📋 Reklamalar ro'yxati")
async def list_broadcasts(message: Message, broadcast_service: BroadcastService, settings: Settings) -> None:
    text, keyboard = await build_broadcasts_page(broadcast_service, settings, 0)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("broadcast:list:"))
async def list_broadcasts_callback(
    callback: CallbackQuery,
    broadcast_service: BroadcastService,
    settings: Settings,
) -> None:
    page = int(callback.data.split(":")[-1])
    if callback.message:
        text, keyboard = await build_broadcasts_page(broadcast_service, settings, page)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:view:"))
async def view_broadcast(callback: CallbackQuery, bot: Bot, broadcast_service: BroadcastService) -> None:
    broadcast_id = int(callback.data.split(":")[-1])
    broadcast = await broadcast_service.get(broadcast_id)
    if broadcast is None:
        await callback.answer("Reklama topilmadi.", show_alert=True)
        return
    try:
        await bot.copy_message(
            chat_id=callback.from_user.id,
            from_chat_id=broadcast.source_chat_id,
            message_id=broadcast.source_message_id,
        )
    except TelegramAPIError:
        await callback.answer("Reklamani ko'rsatib bo'lmadi. Manba xabar o'chirilgan bo'lishi mumkin.", show_alert=True)
        return
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:edit:"))
async def edit_broadcast_start(callback: CallbackQuery, state: FSMContext, broadcast_service: BroadcastService) -> None:
    broadcast_id = int(callback.data.split(":")[-1])
    broadcast = await broadcast_service.get(broadcast_id)
    if broadcast is None:
        await callback.answer("Reklama topilmadi.", show_alert=True)
        return
    if broadcast.status == BroadcastStatus.running:
        await callback.answer("❌ Yuborilayotgan reklamani tahrirlab bo'lmaydi.", show_alert=True)
        return
    await state.set_state(BroadcastStates.editing_post)
    await state.update_data(broadcast_id=broadcast_id)
    if callback.message:
        await callback.message.answer("Yangi reklama postini yuboring.", reply_markup=cancel_admin_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:delete:"))
async def delete_broadcast_prompt(callback: CallbackQuery) -> None:
    broadcast_id = int(callback.data.split(":")[-1])
    if callback.message:
        await callback.message.answer(
            "Rostdan ham ushbu reklamani o'chirmoqchimisiz?",
            reply_markup=confirm_keyboard(f"broadcast:delete_confirm:{broadcast_id}"),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:delete_confirm:"))
async def delete_broadcast_confirm(callback: CallbackQuery, broadcast_service: BroadcastService) -> None:
    broadcast_id = int(callback.data.split(":")[-1])
    ok, text = await broadcast_service.delete(broadcast_id)
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text, reply_markup=broadcast_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:send:"))
async def send_broadcast_prompt(callback: CallbackQuery, broadcast_service: BroadcastService) -> None:
    broadcast_id = int(callback.data.split(":")[-1])
    broadcast = await broadcast_service.get(broadcast_id)
    if broadcast is None:
        await callback.answer("Reklama topilmadi.", show_alert=True)
        return
    if callback.message:
        await callback.message.answer(
            "Ushbu reklamani barcha foydalanuvchilarga yuborishni tasdiqlaysizmi?",
            reply_markup=send_confirm_keyboard(broadcast_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:send_confirm:"))
async def send_broadcast_confirm(
    callback: CallbackQuery,
    bot: Bot,
    broadcast_service: BroadcastService,
) -> None:
    broadcast_id = int(callback.data.split(":")[-1])
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Reklama yuborish boshlandi. Iltimos, kuting.")
    broadcast = await broadcast_service.send_to_all(bot, broadcast_id)
    if callback.message and broadcast:
        await callback.message.answer(
            "📣 Reklama holati\n\n"
            f"Jami user: {broadcast.total_users}\n"
            f"Yuborildi: {broadcast.sent_count}\n"
            f"Xatolik: {broadcast.failed_count}\n"
            f"Status: {broadcast.status.value}\n"
            f"Boshlangan vaqt: {format_dt(broadcast.started_at)}\n"
            f"Tugagan vaqt: {format_dt(broadcast.finished_at)}",
            reply_markup=broadcast_menu_keyboard(),
        )
    await callback.answer()


async def build_broadcasts_page(broadcast_service: BroadcastService, settings: Settings, page: int):
    _, total = await broadcast_service.list_broadcasts(0, settings.page_size)
    page = clamp_page(page, total, settings.page_size)
    broadcasts, total = await broadcast_service.list_broadcasts(page, settings.page_size)
    total_pages = pages_count(total, settings.page_size)
    rows = ["📋 Reklamalar ro'yxati\n"]
    if not broadcasts:
        rows.append("Reklamalar topilmadi.")
    for item in broadcasts:
        rows.append(format_broadcast_card(item))
        rows.append("")
    rows.append(f"Sahifa: {page + 1}/{total_pages}")
    return "\n".join(rows), broadcast_list_keyboard([item.id for item in broadcasts], page, total_pages)


def extract_broadcast_preview(message: Message) -> tuple[str, str]:
    if message.text:
        return "text", message.text[:100]
    if message.caption:
        return detect_content_type(message), message.caption[:100]
    return detect_content_type(message), "-"


def detect_content_type(message: Message) -> str:
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.animation:
        return "animation"
    if message.document:
        return "document"
    return "message"


def format_broadcast_card(broadcast: Broadcast) -> str:
    creator = escape(f"@{broadcast.admin_username}" if broadcast.admin_username else str(broadcast.admin_id or "-"))
    preview = escape(broadcast.preview or "-")
    status = escape(broadcast.status.value)
    return (
        f"📣 Reklama #{broadcast.id}\n"
        f"📌 Holat: {status}\n"
        f"📝 Preview: {preview}\n"
        f"👤 Yaratgan admin: {creator}\n"
        f"📅 Yaratilgan sana: {format_dt(broadcast.created_at)}\n"
        f"📤 Yuborildi: {broadcast.sent_count} / {broadcast.total_users}\n"
        f"❌ Xatolik: {broadcast.failed_count}"
    )
