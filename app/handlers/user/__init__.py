from aiogram import Router

from app.handlers.user import edit_profile, registration, start, survey
from app.middlewares.admin import NonAdminFilter


def get_user_router() -> Router:
    router = Router(name="user")
    router.message.filter(NonAdminFilter())
    router.callback_query.filter(NonAdminFilter())
    router.include_router(start.router)
    router.include_router(registration.router)
    router.include_router(edit_profile.router)
    router.include_router(survey.router)
    return router
