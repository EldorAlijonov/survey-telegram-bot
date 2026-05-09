from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.user_reply import start_survey_keyboard
from app.services.user_service import UserService
from app.states.user_states import RegistrationStates
from app.utils.validators import is_valid_full_name, normalize_phone

router = Router(name="user_registration")


FULL_NAME_FORMAT_ERROR = (
    "<b>Noto‘g‘ri format.</b>\n\n"
    "Iltimos, ma’lumotni ko‘rsatilgan namuna bo‘yicha kiriting.\n\n"
    "Misol:\n<b>Alijonov Eldorjon</b>"
)
PHONE_FORMAT_ERROR = "<b>Telefon raqam noto‘g‘ri.</b>\n\nMisol:\n<b>+998901610714</b>"
FULL_NAME_PROMPT = "<b>Ism familyangizni kiriting.</b>\n\nMisol:\n<b>Alijonov Eldorjon</b>"


@router.message(RegistrationStates.full_name, F.text)
async def get_full_name(message: Message, state: FSMContext, user_service: UserService) -> None:
    full_name = message.text.strip()
    if not is_valid_full_name(full_name):
        await message.answer(FULL_NAME_FORMAT_ERROR)
        return
    await state.update_data(full_name=full_name)
    await finish_registration(message, state, user_service)


@router.message(RegistrationStates.phone, F.contact)
async def get_contact_phone(message: Message, state: FSMContext) -> None:
    if message.contact.user_id and message.from_user and message.contact.user_id != message.from_user.id:
        await message.answer("<b>Noto‘g‘ri format.</b>\n\nIltimos, o‘zingizning kontaktingizni yuboring.")
        return
    await state.update_data(phone=message.contact.phone_number)
    await ask_full_name(message, state)


@router.message(RegistrationStates.phone, F.text)
async def get_phone(message: Message, state: FSMContext) -> None:
    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(PHONE_FORMAT_ERROR)
        return
    await state.update_data(phone=phone)
    await ask_full_name(message, state)


async def ask_full_name(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationStates.full_name)
    await message.answer(FULL_NAME_PROMPT)


async def finish_registration(message: Message, state: FSMContext, user_service: UserService) -> None:
    data = await state.get_data()
    await user_service.update_profile(
        message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        mark_registered=True,
    )
    await state.clear()
    await message.answer(
        "<b>Ma’lumotlaringiz qabul qilindi.</b>\n\n"
        "So‘rovnomani boshlash uchun quyidagi tugmani bosing.",
        reply_markup=start_survey_keyboard(),
    )
