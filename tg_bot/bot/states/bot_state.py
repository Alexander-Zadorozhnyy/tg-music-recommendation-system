from aiogram.fsm.state import StatesGroup, State


class BotStates(StatesGroup):
    waiting_fot_question = State()
    answering_question = State()
    question_type = State()

    step_by_step_active = State()


class RecommendationStates(StatesGroup):
    waiting_free_form = State()
    waiting_tracks_input = State()
