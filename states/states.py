from aiogram.dispatcher.filters.state import State, StatesGroup


class Stages(StatesGroup):
    category = State()
    product = State()
    count = State()
    basket = State()


class Order(StatesGroup):
    phone = State()
    location = State()
    payment_method = State()
    confirmation = State()


class Comment(StatesGroup):
    comment = State()
