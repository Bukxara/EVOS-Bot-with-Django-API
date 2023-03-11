from aiogram import types
from loader import dp
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
from data.config import URL, ADMINS
from states.states import *
from keyboards.default.reply_buttons import *
from keyboards.inline.inline_buttons import *
from api import *

user_data = {}


def count_and_id(data, second=None):
    if not second:
        idx = data.index("_")
        return data[idx+1:]
    idx1 = data.index("_")
    idx2 = data.index("/")
    return [data[idx1+1:idx2], data[idx2+1:]]


@dp.message_handler(text="📥 Корзина", state="*")
async def basket(message: types.Message, state: FSMContext):
    markup = await categories(message.from_user.id)
    result = await basket_button(message.from_user.id)
    await message.answer(text="Выберите категорию", reply_markup=markup)
    if result['is_empty']:
        await message.answer(text="Ваша корзина пусто!")
    else:
        await message.answer(text=f"*В корзине:*\n{result['basket_text']}\n{result['price_text']}",
                             reply_markup=result["button"], parse_mode="Markdown")
    await state.set_state(Stages.category)


@dp.message_handler(text="⬅️ Назад", state="*")
async def menu(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in ["Stages:category", "Comment:comment"]:
        await state.set_state(None)
        await message.answer("Выберите одно из следующих", reply_markup=start)
        await empty_basket(message.from_user.id)
    elif current_state == "Stages:product":
        markup = await categories(message.from_user.id)
        await message.answer("Выберите категорию", reply_markup=markup)
        await state.set_state(Stages.category)
    elif current_state == "Stages:count":
        data = await state.get_data()
        markup = await products(data["category"], message.from_user.id)
        data = await get_category_by_name(data["category"])
        await message.answer_photo(photo=f"{URL}{data[0]['category_image']}", reply_markup=markup)
        await state.set_state(Stages.product)
        user_data[message.from_user.id] = 1
    elif current_state == "Order:phone":
        markup = await categories(message.from_user.id)
        result = await basket_button(message.from_user.id)
        await message.answer("Выберите одно из следующих", reply_markup=start)
        await message.answer(text=f"*В корзине:*\n{result['basket_text']}\n{result['price_text']}",
                             reply_markup=result["button"], parse_mode="Markdown")
    elif current_state == "Order:location":
        await message.answer("""Отправьте или введите ваш номер телефона в формате: +998 ** *** ** ** 
Примечание: Если вы планируете оплатить заказ онлайн с 
помощью Click, либо Payme, пожалуйста, укажите номер 
телефона, на который зарегистрирован аккаунт в 
соответствующем сервисе""", reply_markup=phone_number)
        await state.set_state(Order.phone)
    elif current_state == "Order:payment_method":
        await message.answer("Отправьте 📍 геолокацию или выберите адрес доставки", reply_markup=location)
        await state.set_state(Order.location)
    elif current_state == None:
        await message.answer("Выберите одно из следующих", reply_markup=start)
        await empty_basket(message.from_user.id)


@dp.message_handler(text="🍴 Меню", state="*")
async def menu(message: types.Message, state: FSMContext):
    markup = await categories(message.from_user.id)
    await message.answer("Выберите категорию", reply_markup=markup)
    await state.set_state(Stages.category)


@dp.message_handler(state=Stages.category)
async def send_welcome(message: types.Message, state: FSMContext):
    data = await get_category_by_name(message.text)
    if data:
        await state.update_data(category=message.text)
        markup = await products(message.text, message.from_user.id)
        await message.answer_photo(photo=f"{URL}{data[0]['category_image']}", reply_markup=markup)
        await state.set_state(Stages.product)
    else:
        return await message.reply("Пожалуйста, выберите один из приведённых категорий!")


@dp.message_handler(state=Stages.product)
async def send_welcome(message: types.Message, state: FSMContext):
    data = await get_product_by_name(message.text)
    if data:
        await state.update_data(product=message.text)
        markup = await count_button(1)
        await message.answer("Выберите одно из следующих", reply_markup=product)
        await message.answer_photo(photo=f"{URL}{data[0]['product_image']}",
                                   caption=f"{data[0]['product_description']}\n*Цена:* {data[0]['product_price']} сум", reply_markup=markup, parse_mode="Markdown")
        await state.set_state(Stages.count)
    else:
        return await message.reply("Пожалуйста, выберите один из приведённых продуктов!")


@dp.message_handler(state=Stages.count)
async def send_welcome(message: types.Message, state: FSMContext):
    user_data[message.from_user.id] = 1


async def update_num_text(message: types.Message, new_value: int):
    with suppress(MessageNotModified):
        await message.edit_reply_markup(await count_button(new_value))


@dp.callback_query_handler(Text(startswith="num_"), state=[Stages.count, "*"])
async def callbacks_num(call: types.CallbackQuery, state: FSMContext):
    user_value = user_data.get(call.from_user.id, 1)
    action = call.data.split("_")[1]
    if action == "incr":
        user_data[call.from_user.id] = user_value+1
        await call.answer(f"{user_value+1} шт.")
        await update_num_text(call.message, user_value+1)

    elif action == "decr":
        user_data[call.from_user.id] = user_value-1
        await call.answer(f"{user_value-1} шт.")
        await update_num_text(call.message, user_value-1)

    elif action == "finish":
        await call.answer(f"{user_value} шт.")

    elif action == "add":
        await state.update_data(count=user_value)
        async with state.proxy() as data:
            product = await get_product_by_name(data["product"])
            product_id = product[0]["id"]
            result = await purchase_product(call.from_user.id, product_id, data["count"])
            markup = await products(data["category"], call.from_user.id)
            data = await get_category_by_name(data["category"])
            await call.answer(result)
            await call.message.answer_photo(photo=f"{URL}{data[0]['category_image']}", reply_markup=markup)
            user_data[call.from_user.id] = 1
        await state.set_state(Stages.product)

    await call.answer()


@dp.callback_query_handler(Text(startswith="empty_"), state="*")
async def empty_from_basket(call: types.CallbackQuery, state: FSMContext):
    product_id = count_and_id(call.data)
    await delete_product(call.from_user.id, product_id)
    result = await basket_button(call.from_user.id)
    if result["is_empty"]:
        await call.message.delete()
        await call.message.answer("Ваша корзина пуста!")
    else:
        await call.message.edit_text(f"В корзине:\n{result['basket_text']}\n{result['price_text']}", parse_mode="Markdown")
        await call.message.edit_reply_markup(result["button"])
    await state.set_state(Stages.category)


@dp.callback_query_handler(text="empty", state="*")
async def empty(call: types.CallbackQuery, state: FSMContext):
    result = await empty_basket(call.from_user.id)
    await call.answer(result)
    await call.message.delete()
    await state.set_state(Stages.category)


@dp.callback_query_handler(text="nazad", state="*")
async def empty(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    markup = await categories(call.message.from_user.id)
    await call.message.answer("Выберите категорию", reply_markup=markup)
    await state.set_state(Stages.category)


@dp.callback_query_handler(text="order", state="*")
async def basket(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("""Отправьте или введите ваш номер телефона в формате: +998 ** *** ** ** 
Примечание: Если вы планируете оплатить заказ онлайн с 
помощью Click, либо Payme, пожалуйста, укажите номер 
телефона, на который зарегистрирован аккаунт в 
соответствующем сервисе""", reply_markup=phone_number)
    await state.set_state(Order.phone)


@dp.message_handler(content_types="contact", state=Order.phone)
async def menu(message: types.Message, state: FSMContext):
    await put_number(message.from_user.id, message.contact.phone_number)
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Отправьте 📍 геолокацию или выберите адрес доставки", reply_markup=location)
    await state.set_state(Order.location)


@dp.message_handler(content_types="location", state=Order.location)
async def menu(message: types.Message, state: FSMContext):
    await put_location(message.from_user.id, message.location)
    await state.update_data(location=message.location)
    await message.answer("Пожалуйста, выберите тип оплаты", reply_markup=payment_method)
    await state.set_state(Order.payment_method)


@dp.message_handler(state=Order.payment_method)
async def empty(message: types.Message, state: FSMContext):
    text = await basket_button(message.from_user.id)
    await state.update_data(products=text["basket_text"])
    await state.update_data(payment_method=message.text)
    data = await state.get_data()
    await message.answer(text=f"""*Ваш заказ:*
*Адрес:* {data['location']}\n
{data['products']}
*Тип оплаты:* {data['payment_method']}\n
{text['price_text']}""", reply_markup=confirm, parse_mode='Markdown')
    await state.set_state(Order.confirmation)


@dp.message_handler(text="✅ Подтвердить", state=Order.confirmation)
async def menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = await basket_button(message.from_user.id)
    await post_order(message.from_user.id, data["products"], data["payment_method"], data["location"], text["price_text"], status="Заказ начат")
    result = await all_orders()
    await message.answer(f"""Номер заказа: {result[-1]['id']}\nСтатус: *Новый*\nАдрес: {data['location']}\n
{data['products']}\n
Тип оплаты: *{data['payment_method']}*\n
{text['price_text']}\n
*Ваш заказ оформлен.*
На указанный Вами номер, в ближайшее время будет выставлен счёт.
Расчетное время доставки заказа *30* минут *с момента оплаты счета.*""", reply_markup=start, parse_mode='Markdown')
    await empty_basket(message.from_user.id)
    for admin in ADMINS:
        await dp.bot.send_message(admin, f"""Новый заказ: № {result[-1]['id']}\nСтатус: *Новый*
Номер: {data['phone']}\n
{data['products']}\n
Тип оплаты: *{data['payment_method']}*\n
{text['price_text']}""", parse_mode='Markdown')
        await dp.bot.send_location(admin, latitude=data['location'].latitude, longitude=data['location'].longitude)


@dp.message_handler(text="❌ Отменить", state=Order.confirmation)
async def menu(message: types.Message):
    await message.answer("Выберите одно из следующих", reply_markup=start)
    await empty_basket(message.from_user.id)


@dp.message_handler(text="🛍 Мои заказы", state="*")
async def menu(message: types.Message, state: FSMContext):
    orders = await get_order_by_user(message.from_user.id)
    if orders:
        for order in orders:
            await dp.bot.send_message(message.chat.id, f"""Номер заказа: {order['id']}\nСтатус: *{order['order_status']}*
Адрес: {order['order_address']}\n\n{order['order_items']}\n\nТип оплаты: *{order['payment_method']}*\n
{order['order_sum']}""", parse_mode='Markdown')
    else:
        await message.answer("Вы всё ещё ничего не заказали")


@dp.message_handler(text="✍️ Оставить отзыв", state="*")
async def menu(message: types.Message, state: FSMContext):
    await message.answer("Отправьте ваши отзывы", reply_markup=nazad)
    await state.set_state(Comment.comment)


@dp.message_handler(state=Comment.comment)
async def menu(message: types.Message):
    await comment(message.from_user.id, message.from_user.username, message.text)
    await message.answer("Спасибо за ваш отзыв", reply_markup=start)
