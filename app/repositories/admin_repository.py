from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin


class AdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Admin | None:
        result = await self.session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get(self, admin_id: int) -> Admin | None:
        result = await self.session.execute(select(Admin).where(Admin.id == admin_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        full_name: str | None,
        added_by: int | None,
        username: str | None = None,
        added_by_username: str | None = None,
        is_main: bool = False,
    ) -> Admin:
        admin = Admin(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            added_by=added_by,
            added_by_username=added_by_username,
            is_main=is_main,
        )
        self.session.add(admin)
        await self.session.flush()
        return admin

    async def delete(self, admin: Admin) -> None:
        await self.session.delete(admin)

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[Admin]:
        stmt = select(Admin).order_by(Admin.is_main.desc(), Admin.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        from sqlalchemy import func

        return await self.session.scalar(select(func.count(Admin.id))) or 0
