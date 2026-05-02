from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.survey_repository import SurveyRepository
from app.repositories.user_repository import UserRepository
from app.utils.text import answer_label


class StatsService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)
        self.surveys = SurveyRepository(session)

    async def build_stats_text(self) -> str:
        today = datetime.now().date()
        total = await self.users.count_all()
        today_count = await self.users.count_registered_on(today)
        completed = await self.users.count_completed()
        subscribed = await self.users.count_subscribed()
        top_field, top_count = await self.surveys.top_interested_field()
        time_counts = await self.surveys.convenient_time_counts()
        interest_counts = dict(await self.surveys.interest_counts())
        good = interest_counts.get("good", 0)
        interest_percent = round((good / completed) * 100, 1) if completed else 0
        times = ", ".join(f"{answer_label(key)}: {count}" for key, count in time_counts) or "-"

        return (
            "📊 Statistika\n\n"
            f"Jami foydalanuvchilar: {total}\n"
            f"Bugun ro'yxatdan o'tganlar: {today_count}\n"
            f"So'rovnomani tugatganlar: {completed}\n"
            f"Tugatmaganlar: {max(total - completed, 0)}\n"
            f"Majburiy obunadan o'tganlar: {subscribed}\n"
            f"Eng ko'p tanlangan yo'nalish: {answer_label(top_field)} ({top_count})\n"
            f"Qulay vaqt statistikasi: {times}\n"
            f"Zamonaviy kasblarga qiziqish foizi: {interest_percent}%"
        )
