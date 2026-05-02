from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    full_name = State()
    phone = State()
    address = State()
    education_place = State()


class SurveyStates(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    submit = State()


class EditProfileStates(StatesGroup):
    choosing = State()
    full_name = State()
    phone = State()
    address = State()
    education_place = State()
