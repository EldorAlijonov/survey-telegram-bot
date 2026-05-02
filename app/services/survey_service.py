from datetime import datetime
from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.survey import Survey
from app.repositories.survey_repository import SurveyRepository
from app.repositories.user_repository import UserRepository
from app.utils.text import answer_label


SURVEY_FIELDS = {
    "q1": "interest_level",
    "q2": "school_condition",
    "q3": "extra_learning_intent",
    "q4": "convenient_time",
    "q5": "interested_field",
}


def html_value(value: object | None) -> str:
    if value is None or value == "":
        return "-"
    return escape(str(value))


class SurveyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.surveys = SurveyRepository(session)
        self.users = UserRepository(session)

    async def save_answers(
        self,
        telegram_id: int,
        answers: dict[str, str],
        submitted: bool = False,
        subscribed: bool = False,
    ) -> Survey:
        user = await self.users.get_by_telegram_id(telegram_id)
        if user is None:
            raise ValueError("User not found")
        payload = {field: answers.get(question) for question, field in SURVEY_FIELDS.items()}
        survey = await self.surveys.get_latest_by_user_id(user.id)
        if survey is None:
            survey = await self.surveys.create(user.id, **payload)
        else:
            for key, value in payload.items():
                setattr(survey, key, value)
        if submitted:
            survey.submitted_at = datetime.now()
            user.has_completed_survey = True
            user.is_subscribed = subscribed
        await self.session.commit()
        return survey

    async def mark_submitted(self, telegram_id: int, answers: dict[str, str], subscribed: bool) -> Survey:
        return await self.save_answers(telegram_id, answers, submitted=True, subscribed=subscribed)

    def format_summary(self, user, survey: Survey) -> str:
        full_name = html_value(getattr(user, "full_name", None))
        phone = html_value(getattr(user, "phone", None))
        address = html_value(getattr(user, "address", None))
        education_place = html_value(getattr(user, "education_place", None))
        interest_level = html_value(answer_label(survey.interest_level))
        school_condition = html_value(answer_label(survey.school_condition))
        extra_learning_intent = html_value(answer_label(survey.extra_learning_intent))
        convenient_time = html_value(answer_label(survey.convenient_time))
        interested_field = html_value(answer_label(survey.interested_field))

        return (
            "<b>Siz yuborgan ma’lumotlar:</b>\n\n"
            f"👤 <b>Ism familya:</b> {full_name}\n"
            f"📞 <b>Telefon:</b> {phone}\n"
            f"📍 <b>Manzil:</b> {address}\n"
            f"🏫 <b>Ta’lim muassasasi:</b> {education_place}\n\n"
            "<b>So‘rovnoma javoblari:</b>\n\n"
            f"1. <b>Zamonaviy kasblarga qiziqish:</b> {interest_level}\n"
            f"2. <b>Ta’lim muassasasidagi sharoit:</b> {school_condition}\n"
            f"3. <b>Darsdan tashqari o‘rganish niyati:</b> {extra_learning_intent}\n"
            f"4. <b>Qulay vaqt:</b> {convenient_time}\n"
            f"5. <b>Qiziqqan yo‘nalish:</b> {interested_field}"
        )
