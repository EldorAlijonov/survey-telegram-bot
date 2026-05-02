from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    waiting_post = State()
    editing_post = State()
    confirm = State()
