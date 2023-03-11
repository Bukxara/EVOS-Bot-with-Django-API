from aiogram import types
from loader import dp
from aiogram.dispatcher.filters import Text
from keyboards.default.reply_buttons import *
from keyboards.inline.inline_buttons import *
from api import *


def count_and_id(data, second=None):
    if not second:
        idx = data.index("_")
        return data[idx+1:]
    idx1 = data.index("_")
    idx2 = data.index("/")
    return [data[idx1+1:idx2], data[idx2+1:]]


@dp.message_handler(text="🍴 Меню")
async def menu(message: types.Message):
    markup = await categories_button(message.from_user.id)
    await message.answer("Выберите категорию", reply_markup=markup)


@dp.callback_query_handler(Text(startswith="category_"))
async def products(call: types.CallbackQuery):
    category_id = count_and_id(call.data)
    data = await get_category_by_id(category_id)
    markup = await products_button(category_id)
    await call.message.answer_photo(photo=data["category_image"], reply_markup=markup)


@dp.callback_query_handler(Text(startswith="product_"))
async def product(call: types.CallbackQuery):
    product_id = count_and_id(call.data)
    data = await get_product_by_id(product_id)
    markup = await one_product_button(product_id)
    await call.message.answer_photo(photo=data["product_image"], caption=f"""{data["product_name"]}
Цена: {data["product_price"]}
{data["product_description"]}""", reply_markup=markup)


@dp.callback_query_handler(Text(startswith="quantity_"))
async def products(call: types.CallbackQuery):
    count, product_id = count_and_id(call.data, 2)
    result = await purchase_product(call.from_user.id, product_id, count)
    markup = await categories_button(call.from_user.id)
    await call.answer(result)
    await call.message.answer("Выберите категорию", reply_markup=markup)


@dp.callback_query_handler(text="korzina")
async def basket(call: types.CallbackQuery):
    result = await basket_button(call.from_user.id)
    await call.message.answer(text=f"*В корзине:*\n{result['basket_text']}\n{result['price_text']}",
                              reply_markup=result["button"], parse_mode="Markdown")


@dp.callback_query_handler(text="order")
async def basket(call: types.CallbackQuery):
    username, tg_id = call.from_user.username, call.from_user.id
    user = await post_user(username, tg_id)
    await call.message.answer("""Отправьте или введите ваш номер телефона в формате: +998 ** *** ** ** 
Примечание: Если вы планируете оплатить заказ онлайн с 
помощью Click, либо Payme, пожалуйста, укажите номер 
телефона, на который зарегистрирован аккаунт в 
соответствующем сервисе""", reply_markup=phone_number)


@dp.message_handler(content_types="contact")
async def menu(message: types.Message):
    await put_number(message.from_user.id, message.contact.phone_number)
    await message.answer("Отправьте 📍 геолокацию или выберите адрес доставки", reply_markup=location)


@dp.message_handler(content_types="location")
async def menu(message: types.Message):
    await put_location(message.from_user.id, message.location)
    markup = await payment_method()
    await message.answer("Пожалуйста, выберите тип оплаты", reply_markup=markup)


@dp.callback_query_handler(Text(startswith="pay_"))
async def empty(call: types.CallbackQuery):
    payment_method = count_and_id(call.data)
    user = await post_user(call.from_user.username, call.from_user.id)
    text = await basket_button(call.from_user.id)
    await post_order(call.from_user.id, text['basket_text'], payment_method)
    await call.message.answer(text=f"""*Ваш заказ:*
*Адрес:* {user[0]['user_address']}\n
{text['basket_text']}
Тип оплаты: {payment_method}\n
{text['price_text']}""", reply_markup=confirm, parse_mode='Markdown')


@dp.callback_query_handler(Text(startswith="empty_"))
async def products(call: types.CallbackQuery):
    product_id = count_and_id(call.data)
    await delete_product(call.from_user.id, product_id)
    result = await basket_button(call.from_user.id)
    if result["is_empty"]:
        await call.message.delete()
        await call.message.answer("Ваша корзина пуста!")
    else:
        await call.message.edit_text(result["text"])
        await call.message.edit_reply_markup(result["button"])


@dp.callback_query_handler(text="empty")
async def empty(call: types.CallbackQuery):
    result = await empty_basket(call.from_user.id)
    markup = await categories_button(call.from_user.id)
    await call.answer(result)
    await call.message.edit_reply_markup(markup)


@dp.callback_query_handler(text="nazad_2")
async def empty(call: types.CallbackQuery):
    markup = await categories_button(call.from_user.id)
    await call.message.delete()


@dp.callback_query_handler(text="nazad_3")
async def empty(call: types.CallbackQuery):
    category_id = count_and_id(call.data)
    data = await get_category_by_id(category_id)
    markup = await products_button(category_id)
    await call.message.delete()
    await call.message.answer_photo(photo=data["category_image"], reply_markup=markup)

