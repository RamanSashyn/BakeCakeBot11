from django.db import models
from aiogram.fsm.state import State, StatesGroup

class DeliveryState(StatesGroup):
    waiting_for_address = State()
    waiting_for_comment = State()


class CustomCakeState(StatesGroup):
    waiting_for_text = State()
    waiting_for_address = State()