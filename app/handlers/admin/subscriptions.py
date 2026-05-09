import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.admin_inline import subscription_delete_confirm_keyboard, subscription_detail_keyboard
from app.keyboards.admin_reply import subscription_cancel_keyboard, subscription_manage_keyboard
from app.services.subscription_service import SubscriptionService
from app.states.admin_states import SubscriptionManageStates
from app.utils.callbacks import safe_callback_answer
from app.utils.date_utils import format_dt
from app.utils.pagination import clamp_page, pages_count

logger = logging.getLogger(__name__)
router = Router(name="admin_subscriptions")

SUBSCRIPTION_PAGE_SIZE = 1

CHANNEL_PROMPT = (
    "Ommaviy kanal havolasi yoki username yuboring.\n"
    "Misol: @kanal_username yoki https://t.me/kanal_username"
)
EDIT_CHANNEL_PROMPT = "Yangi kanal havolasi yoki username yuboring."


@router.message(F.text == "➕ Obuna qo'shish")
async def add_subscription_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SubscriptionManageStates.waiting_for_channel_link)
    await state.update_data(subscription_action="add")
    await message.answer(CHANNEL_PROMPT, reply_markup=subscription_cancel_keyboard())


@router.message(SubscriptionManageStates.waiting_for_channel_link, F.text == "❌ Bekor qilish")
async def cancel_subscription_channel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=subscription_manage_keyboard())


@router.message(SubscriptionManageStates.waiting_for_channel_link, F.text)
async def save_subscription_channel(
    message: Message,
    state: FSMContext,
    bot: Bot,
    subscription_service: SubscriptionService,
) -> None:
    data = await state.get_data()
    action = data.get("subscription_action", "add")
    try:
        if action == "edit":
            ok, text = await subscription_service.edit_by_id(bot, int(data["subscription_id"]), message.text)
        else:
            ok, text = await subscription_service.add_channel(bot, message.text)
    except Exception:
        logger.exception("Subscription channel save failed")
        text = "❌ Kanalni saqlashda kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring."

    await state.clear()
    await message.answer(text, reply_markup=subscription_manage_keyboard())


@router.message(SubscriptionManageStates.waiting_for_channel_link)
async def invalid_subscription_channel(message: Message) -> None:
    await message.answer("Iltimos, kanal username yoki havolasini matn ko'rinishida yuboring.")


@router.message(F.text == "📋 Obunalar ro'yxati")
async def subscriptions_list(message: Message, subscription_service: SubscriptionService) -> None:
    text, keyboard = await build_subscriptions_page(subscription_service, 0)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("sub:page:"))
@router.callback_query(F.data.startswith("sub:list:"))
async def subscriptions_list_callback(
    callback: CallbackQuery,
    subscription_service: SubscriptionService,
) -> None:
    page = int(callback.data.split(":")[-1])
    if callback.message:
        text, keyboard = await build_subscriptions_page(subscription_service, page)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("sub:toggle:"))
async def subscription_toggle(
    callback: CallbackQuery,
    subscription_service: SubscriptionService,
) -> None:
    subscription_id = int(callback.data.split(":")[-1])
    ok, text = await subscription_service.toggle_by_id(subscription_id)
    if callback.message:
        page = await subscription_service.page_for_channel(subscription_id, SUBSCRIPTION_PAGE_SIZE)
        new_text, keyboard = await build_subscriptions_page(subscription_service, page)
        await callback.message.edit_text(new_text, reply_markup=keyboard)
    await safe_callback_answer(callback, text, show_alert=True)


@router.callback_query(F.data.startswith("sub:edit:"))
async def subscription_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    subscription_id = int(callback.data.split(":")[-1])
    await state.set_state(SubscriptionManageStates.waiting_for_channel_link)
    await state.update_data(subscription_action="edit", subscription_id=subscription_id)
    if callback.message:
        await callback.message.answer(EDIT_CHANNEL_PROMPT, reply_markup=subscription_cancel_keyboard())
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("sub:delete:"))
async def subscription_delete_prompt(callback: CallbackQuery, subscription_service: SubscriptionService) -> None:
    subscription_id = int(callback.data.split(":")[-1])
    subscription = await subscription_service.get_channel(subscription_id)
    if subscription is None:
        await safe_callback_answer(callback, "Kanal topilmadi.", show_alert=True)
        return
    if callback.message:
        await callback.message.edit_text(
            "Rostdan ham ushbu kanalni o'chirmoqchimisiz?\n\n"
            f"📢 {escape(subscription.title)}\n"
            f"🔗 @{escape(subscription.channel_username)}",
            reply_markup=subscription_delete_confirm_keyboard(subscription_id),
        )
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("sub:delete_confirm:"))
async def subscription_delete_confirm(callback: CallbackQuery, subscription_service: SubscriptionService) -> None:
    subscription_id = int(callback.data.split(":")[-1])
    page = await subscription_service.page_for_channel(subscription_id, SUBSCRIPTION_PAGE_SIZE)
    ok, text = await subscription_service.delete_by_id(subscription_id)
    if callback.message:
        new_text, keyboard = await build_subscriptions_page(subscription_service, page)
        await callback.message.edit_text(new_text, reply_markup=keyboard)
    await safe_callback_answer(callback, text, show_alert=True)


@router.callback_query(F.data.startswith("sub:delete_cancel:"))
async def subscription_delete_cancel(callback: CallbackQuery, subscription_service: SubscriptionService) -> None:
    subscription_id = int(callback.data.split(":")[-1])
    page = await subscription_service.page_for_channel(subscription_id, SUBSCRIPTION_PAGE_SIZE)
    if callback.message:
        text, keyboard = await build_subscriptions_page(subscription_service, page)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_callback_answer(callback, "O'chirish bekor qilindi.")


async def build_subscriptions_page(subscription_service: SubscriptionService, page: int):
    _, total = await subscription_service.list_channels(0, SUBSCRIPTION_PAGE_SIZE)
    page = clamp_page(page, total, SUBSCRIPTION_PAGE_SIZE)
    channels, total = await subscription_service.list_channels(page, SUBSCRIPTION_PAGE_SIZE)
    total_pages = pages_count(total, SUBSCRIPTION_PAGE_SIZE)
    if not channels:
        return "📢 Majburiy obuna\n\nObunalar topilmadi.", None

    channel = channels[0]
    status = "✅ Aktiv" if channel.is_active else "❌ Noaktiv"
    title = escape(channel.title)
    username = escape(channel.channel_username)
    text = (
        "📢 Majburiy obuna\n\n"
        f"{page + 1}/{total}-kanal\n\n"
        f"📌 Nomi: {title}\n"
        f"🔗 Username: @{username}\n"
        f"📍 Holat: {status}\n"
        f"🆔 Chat ID: {channel.chat_id or '-'}\n"
        f"📅 Qo'shilgan sana: {format_dt(channel.created_at)}"
    )
    return text, subscription_detail_keyboard(channel.id, channel.is_active, page, total_pages)
