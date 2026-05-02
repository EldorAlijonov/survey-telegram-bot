from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.repositories.admin_repository import AdminRepository


async def sync_main_admins(session: AsyncSession, settings: Settings) -> None:
    repo = AdminRepository(session)
    for telegram_id in settings.main_admin_ids:
        admin = await repo.get_by_telegram_id(telegram_id)
        if admin is None:
            await repo.create(
                telegram_id=telegram_id,
                full_name="Asosiy admin",
                added_by=None,
                is_main=True,
            )
        elif not admin.is_main:
            admin.is_main = True
    await session.commit()
