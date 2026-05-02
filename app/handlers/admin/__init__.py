from aiogram import Router

from app.handlers.admin import admins, broadcast, export, panel, start, statistics, subscriptions, users
from app.middlewares.admin import AdminFilter


def get_admin_router() -> Router:
    router = Router(name="admin")
    router.message.filter(AdminFilter())
    router.callback_query.filter(AdminFilter())
    router.include_router(start.router)
    router.include_router(subscriptions.router)
    router.include_router(panel.router)
    router.include_router(admins.router)
    router.include_router(statistics.router)
    router.include_router(users.router)
    router.include_router(export.router)
    router.include_router(broadcast.router)
    return router
