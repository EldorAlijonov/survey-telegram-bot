from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    full_name = State()
    phone = State()


class SurveyStates(StatesGroup):
    q1 = State()
    q4 = State()
    q5 = State()
    submit = State()


class EditProfileStates(StatesGroup):
    choosing = State()
    full_name = State()
    phone = State()
