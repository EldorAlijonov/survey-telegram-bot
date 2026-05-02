from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def admin_panel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Adminlar"), KeyboardButton(text="📢 Majburiy obunalar")],
            [KeyboardButton(text="📣 Reklama"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="👥 Foydalanuvchilar"), KeyboardButton(text="📥 Excel yuklab olish")],
        ],
        resize_keyboard=True,
    )


def admin_manage_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Admin qo'shish"), KeyboardButton(text="📋 Adminlar ro'yxati")],
            [KeyboardButton(text="⬅️ Ortga"), KeyboardButton(text="🏠 Admin panel")],
        ],
        resize_keyboard=True,
    )


def subscription_manage_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Obuna qo'shish"), KeyboardButton(text="📋 Obunalar ro'yxati")],
            [KeyboardButton(text="⬅️ Ortga"), KeyboardButton(text="🏠 Admin panel")],
        ],
        resize_keyboard=True,
    )


def subscription_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def broadcast_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Reklama yaratish"), KeyboardButton(text="📋 Reklamalar ro'yxati")],
            [KeyboardButton(text="✏️ Reklamani tahrirlash"), KeyboardButton(text="🗑 Reklamani o'chirish")],
            [KeyboardButton(text="🚀 Reklama yuborish")],
            [KeyboardButton(text="⬅️ Ortga"), KeyboardButton(text="🏠 Admin panel")],
        ],
        resize_keyboard=True,
    )


def cancel_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")],
            [KeyboardButton(text="🏠 Admin panel")],
        ],
        resize_keyboard=True,
    )


def date_select_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Bugun"), KeyboardButton(text="Kecha")],
            [KeyboardButton(text="Sana kiritish")],
            [KeyboardButton(text="⬅️ Ortga"), KeyboardButton(text="🏠 Admin panel")],
        ],
        resize_keyboard=True,
    )


def export_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Bugungi ro'yxat")],
            [KeyboardButton(text="Barcha so'rovnomadan o'tganlar")],
            [KeyboardButton(text="Sana bo'yicha")],
            [KeyboardButton(text="⬅️ Ortga"), KeyboardButton(text="🏠 Admin panel")],
        ],
        resize_keyboard=True,
    )
