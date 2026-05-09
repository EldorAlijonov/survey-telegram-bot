from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.handlers.user.survey import start_survey
from app.keyboards.user_reply import after_finish_keyboard, cancel_edit_keyboard, edit_profile_keyboard
from app.services.user_service import UserService
from app.states.user_states import EditProfileStates
from app.utils.validators import is_valid_full_name, normalize_phone

router = Router(name="user_edit_profile")


PHONE_FORMAT_ERROR = "<b>Telefon raqam noto‘g‘ri.</b>\n\nMisol:\n<b>+998901610714</b>"
GENERIC_FORMAT_ERROR = "<b>Noto‘g‘ri format.</b>\n\nIltimos, ma’lumotni ko‘rsatilgan namuna bo‘yicha kiriting."


@router.message(F.text.in_({"✏️ Ma’lumotlarni tahrirlash", "✏️ Ma'lumotlarni tahrirlash"}))
async def edit_profile_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(EditProfileStates.choosing)
    await message.answer(
        "<b>Qaysi ma’lumotni tahrirlaysiz?</b>\n\nKerakli bo‘limni tanlang.",
        reply_markup=edit_profile_keyboard(),
    )


@router.message(EditProfileStates.choosing, F.text == "⬅️ Ortga")
async def back_to_user_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("<b>Asosiy menyu.</b>", reply_markup=after_finish_keyboard())


@router.message(
    EditProfileStates.choosing,
    F.text.in_({"Ism familya", "Telefon raqam"}),
)
async def choose_edit_field(message: Message, state: FSMContext) -> None:
    mapping = {
        "Ism familya": (EditProfileStates.full_name, "<b>Yangi ism familyangizni kiriting.</b>"),
        "Telefon raqam": (
            EditProfileStates.phone,
            "<b>Yangi telefon raqamingizni kiriting.</b>\n\nMisol:\n<b>+998901610714</b>",
        ),
    }
    item = mapping[message.text]
    await state.set_state(item[0])
    await message.answer(item[1], reply_markup=cancel_edit_keyboard())


@router.message(EditProfileStates.choosing, F.text.in_({"So‘rovnoma javoblari", "So'rovnoma javoblari"}))
async def edit_survey_answers(message: Message, state: FSMContext, user_service: UserService) -> None:
    await start_survey(message, state, user_service)


@router.message(F.text == "❌ Bekor qilish")
async def cancel_edit_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "<b>Tahrirlash bekor qilindi.</b>\n\nAsosiy menyuga qaytdingiz.",
        reply_markup=after_finish_keyboard(),
    )


@router.message(EditProfileStates.full_name, F.text)
async def update_full_name(message: Message, state: FSMContext, user_service: UserService) -> None:
    value = message.text.strip()
    if not is_valid_full_name(value):
        await message.answer(GENERIC_FORMAT_ERROR)
        return
    await user_service.update_profile(message.from_user.id, full_name=value)
    await state.clear()
    await message.answer("<b>Ism familya yangilandi.</b>", reply_markup=after_finish_keyboard())


@router.message(EditProfileStates.phone, F.contact)
async def update_contact_phone(message: Message, state: FSMContext, user_service: UserService) -> None:
    await user_service.update_profile(message.from_user.id, phone=message.contact.phone_number)
    await state.clear()
    await message.answer("<b>Telefon raqam yangilandi.</b>", reply_markup=after_finish_keyboard())


@router.message(EditProfileStates.phone, F.text)
async def update_phone(message: Message, state: FSMContext, user_service: UserService) -> None:
    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(PHONE_FORMAT_ERROR)
        return
    await user_service.update_profile(message.from_user.id, phone=phone)
    await state.clear()
    await message.answer("<b>Telefon raqam yangilandi.</b>", reply_markup=after_finish_keyboard())

