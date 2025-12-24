from aiogram.fsm.state import State, StatesGroup


class CommandState(StatesGroup):
    waiting_for_command = State()