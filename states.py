from aiogram.fsm.state import State, StatesGroup


class SaveInfo(StatesGroup):
    send_phone = State()
    has_pass = State()
    send_pass = State()

class SendText(StatesGroup):
    send_text = State()  

class EnterCode(StatesGroup):
    first = State()  
    second = State()
    third = State()
    fourth = State()
    fifth = State()

class MultiAnswer(StatesGroup):
    msg = State()