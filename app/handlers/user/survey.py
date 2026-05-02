import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.user_inline import submit_survey_keyboard, subscription_keyboard, survey_question_keyboard
from app.keyboards.user_reply import after_finish_keyboard, remove_keyboard
from app.services.subscription_service import SubscriptionService
from app.services.survey_service import SurveyService
from app.services.user_service import UserService
from app.states.user_states import SurveyStates

router = Router(name="user_survey")
logger = logging.getLogger(__name__)

QUESTIONS = {
    "q1": (
        "<b>Savol 1/5</b>\n\n"
        "<b>Sizning zamonaviy kasblarga qiziqishingiz qanday?</b>\n\n"
        "Dasturlash, grafik dizayn, robototexnika, sun’iy intellekt, SMM"
    ),
    "q2": (
        "<b>Savol 2/5</b>\n\n"
        "<b>Ta’lim muassasangizda zamonaviy kasblarni o‘rganish uchun sharoit qanday?</b>"
    ),
    "q3": (
        "<b>Savol 3/5</b>\n\n"
        "<b>Darsdan tashqari zamonaviy kasblarni o‘rganish niyatingiz bormi?</b>"
    ),
    "q4": (
        "<b>Savol 4/5</b>\n\n"
        "<b>Maktabdan tashqari qo‘shimcha darslarga qatnashish uchun sizga qulay vaqt qaysi?</b>"
    ),
    "q5": "<b>Savol 5/5</b>\n\n<b>Zamonaviy kasblarning qaysi biri siz uchun qiziqarli?</b>",
}

STATE_BY_QUESTION = {
    "q1": SurveyStates.q1,
    "q2": SurveyStates.q2,
    "q3": SurveyStates.q3,
    "q4": SurveyStates.q4,
    "q5": SurveyStates.q5,
}

NEXT_QUESTION = {"q1": "q2", "q2": "q3", "q3": "q4", "q4": "q5"}


async def send_question(message: Message, state: FSMContext, question: str) -> None:
    await state.set_state(STATE_BY_QUESTION[question])
    await message.answer(QUESTIONS[question], reply_markup=survey_question_keyboard(question))


@router.message(F.text.in_({"🚀 So‘rovnomadan o‘tish", "🚀 So'rovnomadan o'tish", "🚀 So'rovnomani boshlash"}))
async def start_survey(message: Message, state: FSMContext, user_service: UserService) -> None:
    user = await user_service.get_profile_with_surveys(message.from_user.id)
    if user is None or not user.is_registered:
        await message.answer("<b>Noto‘g‘ri format.</b>\n\nAvval ro‘yxatdan o‘tishingiz kerak. /start ni bosing.")
        return
    await state.clear()
    await state.update_data(answers={})
    await message.answer(
        "<b>Diqqat, so‘rovnoma boshlandi!</b>\n\nIltimos, savollarga diqqat bilan javob bering.",
        reply_markup=remove_keyboard,
    )
    await send_question(message, state, "q1")


@router.callback_query(F.data.startswith("survey:q"))
async def survey_answer(callback: CallbackQuery, state: FSMContext) -> None:
    parts = (callback.data or "").split(":")
    if len(parts) != 3 or parts[0] != "survey":
        await callback.answer("Noto‘g‘ri tugma.", show_alert=True)
        return
    question, answer = parts[1], parts[2]
    if question not in QUESTIONS:
        await callback.answer("Noto‘g‘ri savol.", show_alert=True)
        return

    data = await state.get_data()
    answers = dict(data.get("answers", {}))
    answers[question] = answer
    await state.update_data(answers=answers)

    next_question = NEXT_QUESTION.get(question)
    if callback.message is None:
        await callback.answer()
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    if next_question:
        await state.set_state(STATE_BY_QUESTION[next_question])
        await callback.message.answer(
            QUESTIONS[next_question],
            reply_markup=survey_question_keyboard(next_question),
        )
    else:
        await state.set_state(SurveyStates.submit)
        await callback.message.answer(
            "<b>So‘rovnoma tugadi.</b>\n\n"
            "Javoblaringizni yuborish uchun quyidagi tugmani bosing.",
            reply_markup=submit_survey_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "survey:submit")
async def submit_survey(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    subscription_service: SubscriptionService,
    survey_service: SurveyService,
    user_service: UserService,
) -> None:
    data = await state.get_data()
    answers = data.get("answers", {})
    if len(answers) < 5:
        await callback.answer("Barcha savollarga javob bering.", show_alert=True)
        return
    if callback.from_user is None or callback.message is None:
        return
    await callback.message.edit_reply_markup(reply_markup=None)

    try:
        subs = await subscription_service.get_all_active()
    except Exception:
        logger.exception("Active subscriptions fetch failed")
        await callback.answer("Obuna kanallarini olishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.", show_alert=True)
        return

    if not subs:
        await finish_survey(callback, state, survey_service, user_service, answers, subscribed=False)
        return

    await callback.message.answer(
        subscription_message(len(subs)),
        reply_markup=subscription_keyboard(subs),
    )
    await callback.answer()


@router.callback_query(F.data == "check_subs")
async def check_all_subs(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    subscription_service: SubscriptionService,
    survey_service: SurveyService,
    user_service: UserService,
) -> None:
    data = await state.get_data()
    answers = data.get("answers", {})
    if callback.from_user is None or callback.message is None:
        return
    if len(answers) < 5:
        await callback.answer("So‘rovnoma javoblari topilmadi. Iltimos, so‘rovnomani qaytadan boshlang.", show_alert=True)
        return

    try:
        subs = await subscription_service.get_all_active()
    except Exception:
        logger.exception("Active subscriptions fetch failed")
        await callback.answer("Obuna kanallarini olishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.", show_alert=True)
        return
    await callback.answer()

    if not subs:
        await callback.message.edit_reply_markup(reply_markup=None)
        await finish_survey(callback, state, survey_service, user_service, answers, subscribed=False, answer_callback=False)
        return

    not_subscribed = []
    for sub in subs:
        chat_id = sub.chat_id or f"@{sub.channel_username}"
        if not await subscription_service.check_user(bot, callback.from_user.id, chat_id):
            not_subscribed.append(sub)

    if not_subscribed:
        await callback.message.answer(
            "<b>❌ Siz barcha kanallarga obuna bo‘lmadingiz!</b>\n\n"
            "Iltimos, avval quyidagi kanallarga obuna bo‘ling va qayta tekshiring.",
            reply_markup=subscription_keyboard(not_subscribed),
        )
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    await finish_survey(callback, state, survey_service, user_service, answers, subscribed=True, answer_callback=False)


def subscription_message(count: int) -> str:
    if count >= 3:
        return f"<b>{count} ta kanalga obuna bo‘lishingiz kerak:</b>"
    return "<b>So‘rovnomani yakunlash uchun quyidagi kanallarga obuna bo‘ling:</b>"


async def finish_survey(
    callback: CallbackQuery,
    state: FSMContext,
    survey_service: SurveyService,
    user_service: UserService,
    answers: dict[str, str],
    subscribed: bool,
    answer_callback: bool = True,
) -> None:
    survey = await survey_service.mark_submitted(callback.from_user.id, answers, subscribed=subscribed)
    user = await user_service.get_profile_with_surveys(callback.from_user.id)
    await state.clear()
    if callback.message:
        await callback.message.answer(survey_service.format_summary(user, survey), reply_markup=remove_keyboard)
        await callback.message.answer(
            "<b>Rahmat!</b>\n\nSo'rovnomangiz muvaffaqiyatli qabul qilindi. \n",
            "<b>Savol va murojaatlar uchun @UstozRobotnik ga murojaat qiling.</b>",
            reply_markup=after_finish_keyboard(),
        )
    if answer_callback:
        await callback.answer()
