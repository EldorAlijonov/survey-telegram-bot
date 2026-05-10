from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def pagination_buttons(prefix: str, page: int, total_pages: int) -> list[InlineKeyboardButton]:
    buttons: list[InlineKeyboardButton] = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"{prefix}:{page - 1}"))
    if page + 1 < total_pages:
        buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"{prefix}:{page + 1}"))
    return buttons


def pagination_keyboard(prefix: str, page: int, total_pages: int) -> InlineKeyboardMarkup | None:
    buttons = pagination_buttons(prefix, page, total_pages)
    if not buttons:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def page_number_buttons(prefix: str, current_page: int, total_pages: int, row_width: int = 5) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for page in range(total_pages):
        text = f"[{page + 1}]" if page == current_page else str(page + 1)
        row.append(InlineKeyboardButton(text=text, callback_data=f"{prefix}:{page}"))
        if len(row) == row_width:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


def users_list_keyboard(user_ids: list[int], scope: str, page: int, total_pages: int) -> InlineKeyboardMarkup | None:
    rows: list[list[InlineKeyboardButton]] = []
    for telegram_id in user_ids:
        rows.append(
            [InlineKeyboardButton(text=f"🗑 O'chirish {telegram_id}", callback_data=f"users:delete:{telegram_id}:{scope}:{page}")]
        )
    rows.extend(page_number_buttons(f"users:list:{scope}", page, total_pages))
    if not rows:
        return None
    return InlineKeyboardMarkup(inline_keyboard=rows)


def user_delete_confirm_keyboard(telegram_id: int, scope: str, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"users:delete_confirm:{telegram_id}:{scope}:{page}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"users:delete_cancel:{scope}:{page}")],
        ]
    )


def admins_list_keyboard(admin_ids: list[tuple[int, bool]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for admin_id, can_delete in admin_ids:
        if can_delete:
            rows.append([InlineKeyboardButton(text=f"🗑 O'chirish #{admin_id}", callback_data=f"admin:delete:{admin_id}")])
    nav = pagination_buttons("admins:list", page, total_pages)
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=confirm_data)],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=cancel_data)],
        ]
    )


def subscription_detail_keyboard(subscription_id: int, is_active: bool, page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    toggle_text = "❌ Noaktiv qilish" if is_active else "✅ Aktiv qilish"
    rows.append([InlineKeyboardButton(text=toggle_text, callback_data=f"sub:toggle:{subscription_id}")])
    rows.append(
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"sub:edit:{subscription_id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"sub:delete:{subscription_id}"),
        ]
    )
    nav = pagination_buttons("sub:page", page, total_pages)
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def subscription_delete_confirm_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"sub:delete_confirm:{subscription_id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"sub:delete_cancel:{subscription_id}")],
        ]
    )


def broadcast_actions_keyboard(broadcast_id: int, include_list: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="👁 Ko'rish", callback_data=f"broadcast:view:{broadcast_id}"),
            InlineKeyboardButton(text="🚀 Yuborish", callback_data=f"broadcast:send:{broadcast_id}"),
        ],
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"broadcast:edit:{broadcast_id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"broadcast:delete:{broadcast_id}"),
        ],
    ]
    if include_list:
        rows.append([InlineKeyboardButton(text="📋 Ro'yxatga qaytish", callback_data="broadcast:list:0")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def broadcast_list_keyboard(broadcast_ids: list[int], page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for broadcast_id in broadcast_ids:
        rows.append(
            [
                InlineKeyboardButton(text=f"👁 #{broadcast_id}", callback_data=f"broadcast:view:{broadcast_id}"),
                InlineKeyboardButton(text="🚀", callback_data=f"broadcast:send:{broadcast_id}"),
                InlineKeyboardButton(text="✏️", callback_data=f"broadcast:edit:{broadcast_id}"),
                InlineKeyboardButton(text="🗑", callback_data=f"broadcast:delete:{broadcast_id}"),
            ]
        )
    nav = pagination_buttons("broadcast:list", page, total_pages)
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def send_confirm_keyboard(broadcast_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Ha, yuborish", callback_data=f"broadcast:send_confirm:{broadcast_id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")],
        ]
    )
