from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.user_reply import contact_keyboard, remove_keyboard, start_survey_keyboard
from app.services.user_service import UserService
from app.states.user_states import RegistrationStates
from app.utils.validators import is_valid_full_name, normalize_phone

router = Router(name="user_registration")


FULL_NAME_FORMAT_ERROR = (
    "<b>Noto‘g‘ri format.</b>\n\n"
    "Iltimos, ma’lumotni ko‘rsatilgan namuna bo‘yicha kiriting.\n\n"
    "Misol:\n<b>Alijonov Eldorjon</b>"
)
PHONE_PROMPT = (
    "<b>Telefon raqamingizni kiriting.</b>\n\n"
    "Siz bilan bog‘lanishimiz uchun hozirda faol bo‘lgan telefon raqam kerak.\n\n"
    "Misol:\n<b>+998901610714</b>"
)
PHONE_FORMAT_ERROR = "<b>Telefon raqam noto‘g‘ri.</b>\n\nMisol:\n<b>+998901610714</b>"
ADDRESS_PROMPT = (
    "<b>Yashash manzilingizni kiriting.</b>\n\n"
    "Misol:\n<b>Farg‘ona viloyati Bag‘dod tumani Do‘rmoncha qishlog‘i</b>"
)
EDUCATION_PROMPT = (
    "<b>Ta’lim muassasangiz raqami yoki nomini kiriting.</b>\n\n"
    "Misol:\n<b>60-maktab</b> yoki <b>E’tirof xalqaro maktabi</b>"
)


@router.message(RegistrationStates.full_name, F.text)
async def get_full_name(message: Message, state: FSMContext) -> None:
    full_name = message.text.strip()
    if not is_valid_full_name(full_name):
        await message.answer(FULL_NAME_FORMAT_ERROR)
        return
    await state.update_data(full_name=full_name)
    await state.set_state(RegistrationStates.phone)
    await message.answer(PHONE_PROMPT, reply_markup=contact_keyboard())


@router.message(RegistrationStates.phone, F.contact)
async def get_contact_phone(message: Message, state: FSMContext) -> None:
    if message.contact.user_id and message.from_user and message.contact.user_id != message.from_user.id:
        await message.answer("<b>Noto‘g‘ri format.</b>\n\nIltimos, o‘zingizning kontaktingizni yuboring.")
        return
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegistrationStates.address)
    await message.answer(ADDRESS_PROMPT, reply_markup=remove_keyboard)


@router.message(RegistrationStates.phone, F.text)
async def get_phone(message: Message, state: FSMContext) -> None:
    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(PHONE_FORMAT_ERROR)
        return
    await state.update_data(phone=phone)
    await state.set_state(RegistrationStates.address)
    await message.answer(ADDRESS_PROMPT, reply_markup=remove_keyboard)


@router.message(RegistrationStates.address, F.text)
async def get_address(message: Message, state: FSMContext) -> None:
    address = message.text.strip()
    if len(address) < 5:
        await message.answer(
            "<b>Noto‘g‘ri format.</b>\n\nIltimos, ma’lumotni ko‘rsatilgan namuna bo‘yicha kiriting."
        )
        return
    await state.update_data(address=address)
    await state.set_state(RegistrationStates.education_place)
    await message.answer(EDUCATION_PROMPT)


@router.message(RegistrationStates.education_place, F.text)
async def get_education_place(message: Message, state: FSMContext, user_service: UserService) -> None:
    education_place = message.text.strip()
    if len(education_place) < 2:
        await message.answer(
            "<b>Noto‘g‘ri format.</b>\n\nIltimos, ma’lumotni ko‘rsatilgan namuna bo‘yicha kiriting."
        )
        return
    data = await state.get_data()
    await user_service.update_profile(
        message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        address=data["address"],
        education_place=education_place,
        mark_registered=True,
    )
    await state.clear()
    await message.answer(
        "<b>Ma’lumotlaringiz qabul qilindi.</b>\n\n"
        "So‘rovnomani boshlash uchun quyidagi tugmani bosing.",
        reply_markup=start_survey_keyboard(),
    )
