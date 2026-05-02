from html import escape

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.user_reply import after_finish_keyboard, remove_keyboard, start_survey_keyboard
from app.middlewares.admin import NonAdminFilter
from app.services.user_service import UserService
from app.states.user_states import RegistrationStates

router = Router(name="user_start")
router.message.filter(NonAdminFilter())


FULL_NAME_PROMPT = "<b>Ism familyangizni kiriting.</b>\n\nMisol:\n<b>Alijonov Eldorjon</b>"


@router.message(CommandStart())
async def user_start(message: Message, state: FSMContext, user_service: UserService) -> None:
    await state.clear()
    user = await user_service.get_or_create(message.from_user)
    name = escape(message.from_user.full_name if message.from_user else "aziz foydalanuvchi")
    greeting = (
        f"<b>Assalomu alaykum, {name}!</b>\n\n"
        "Ushbu botning vazifasi — <b>o‘quvchi yoshlarni zamonaviy kasblarga yo‘naltirish</b> "
        "va ularning qiziqishlarini so‘rovnoma orqali aniqlash."
    )
    await message.answer(greeting, reply_markup=remove_keyboard)

    if user.has_completed_survey:
        await message.answer("<b>Quyidagi menyudan kerakli bo‘limni tanlang.</b>", reply_markup=after_finish_keyboard())
        return

    if user.is_registered:
        await message.answer(
            "<b>Ma’lumotlaringiz qabul qilindi.</b>\n\n"
            "So‘rovnomani boshlash uchun quyidagi tugmani bosing.",
            reply_markup=start_survey_keyboard(),
        )
        return

    await state.set_state(RegistrationStates.full_name)
    await message.answer(FULL_NAME_PROMPT)


@router.message(
    StateFilter(
        RegistrationStates.full_name,
        RegistrationStates.phone,
        RegistrationStates.address,
        RegistrationStates.education_place,
    ),
    F.text == "❌ Bekor qilish",
)
async def cancel_user_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("<b>Jarayon bekor qilindi.</b>", reply_markup=remove_keyboard)
