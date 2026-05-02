from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Kontakt yuborish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def start_survey_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 So‘rovnomadan o‘tish")],
        ],
        resize_keyboard=True,
    )


def after_finish_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ Ma’lumotlarni tahrirlash")],
        ],
        resize_keyboard=True,
    )


def edit_profile_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ism familya"), KeyboardButton(text="Telefon raqam")],
            [KeyboardButton(text="Yashash manzili"), KeyboardButton(text="Ta’lim muassasasi")],
            [KeyboardButton(text="So‘rovnoma javoblari")],
            [KeyboardButton(text="❌ Bekor qilish")],
            [KeyboardButton(text="⬅️ Ortga")],
        ],
        resize_keyboard=True,
    )


def cancel_edit_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


remove_keyboard = ReplyKeyboardRemove()
