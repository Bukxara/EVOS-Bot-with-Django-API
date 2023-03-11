from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp
from keyboards.default.reply_buttons import *
from api import post_user, empty_basket


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message):
    username, tg_id = message.from_user.username, message.from_user.id
    await post_user(username, tg_id)
    await message.answer("Выберите одно из следующих", reply_markup=start)
    await empty_basket(message.from_user.id)
