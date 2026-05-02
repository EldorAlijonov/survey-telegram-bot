from aiogram.fsm.state import State, StatesGroup


class AdminManageStates(StatesGroup):
    add_admin = State()


class AdminUsersStates(StatesGroup):
    custom_date = State()


class AdminExportStates(StatesGroup):
    custom_date = State()


class SubscriptionManageStates(StatesGroup):
    waiting_for_channel_link = State()
