from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models.subscription import Subscription


def build_inline_keyboard(buttons: list[tuple[str, str]], row_width: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.button(text=text, callback_data=callback_data)
    builder.adjust(row_width)
    return builder.as_markup()


def survey_question_keyboard(question: str) -> InlineKeyboardMarkup:
    buttons: dict[str, list[tuple[str, str]]] = {
        "q1": [("🟢 Yaxshi", "survey:q1:good"), ("🔴 Unchalik emas", "survey:q1:bad")],
        "q2": [("🟢 Yaxshi", "survey:q2:good"), ("🔴 Unchalik emas", "survey:q2:bad")],
        "q3": [("🟢 Ha", "survey:q3:yes"), ("🔴 Yo‘q", "survey:q3:no")],
        "q4": [
            ("🟢 08:00 dan 12:00 gacha", "survey:q4:morning"),
            ("🟢 12:00 dan 18:00 gacha", "survey:q4:afternoon"),
        ],
        "q5": [
            ("🟢 Web dasturlash", "survey:q5:web"),
            ("🟢 Robototexnika", "survey:q5:robotics"),
            ("🟢 Sun’iy intellekt", "survey:q5:ai"),
            ("🟢 Grafik dizayn", "survey:q5:design"),
            ("🟢 Kompyuter savodxonligi", "survey:q5:computer"),
            ("🟢 Ingliz tili", "survey:q5:english"),
        ],
    }
    return build_inline_keyboard(buttons[question], row_width=2)


def submit_survey_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📤 Yuborish", callback_data="survey:submit")]]
    )


def subscription_keyboard(subs: list[Subscription]) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=f"📢 {sub.title}", url=sub.channel_url)]
        for sub in subs
    ]
    keyboard.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
