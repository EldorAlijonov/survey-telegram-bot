from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.survey import Survey


class SurveyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_latest_by_user_id(self, user_id: int) -> Survey | None:
        result = await self.session.execute(
            select(Survey).where(Survey.user_id == user_id).order_by(Survey.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, **answers: str | None) -> Survey:
        survey = Survey(user_id=user_id, **answers)
        self.session.add(survey)
        await self.session.flush()
        return survey

    async def top_interested_field(self) -> tuple[str | None, int]:
        result = await self.session.execute(
            select(Survey.interested_field, func.count(Survey.id).label("count"))
            .where(Survey.submitted_at.is_not(None))
            .group_by(Survey.interested_field)
            .order_by(desc("count"))
            .limit(1)
        )
        row = result.first()
        return (row[0], row[1]) if row else (None, 0)

    async def convenient_time_counts(self) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(Survey.convenient_time, func.count(Survey.id))
            .where(Survey.submitted_at.is_not(None))
            .group_by(Survey.convenient_time)
        )
        return [(str(row[0]), row[1]) for row in result.all()]

    async def interest_counts(self) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(Survey.interest_level, func.count(Survey.id))
            .where(Survey.submitted_at.is_not(None))
            .group_by(Survey.interest_level)
        )
        return [(str(row[0]), row[1]) for row in result.all()]
