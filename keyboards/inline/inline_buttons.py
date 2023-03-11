from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from api import *


def pretty_numbers(num):
    quantity = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣",
                5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣"}
    return quantity.get(num)


async def categories_button(tg_id=None):
    button = InlineKeyboardMarkup(row_width=2)
    categories = await all_categories()
    for category in categories:
        button.insert(
            InlineKeyboardButton(text=category["category_name"], callback_data=f"category_{category['id']}"))
    basket = await get_basket(tg_id)
    if basket:
        button.add(
            InlineKeyboardButton(text="📥 Корзина", callback_data="korzina"))

    return button


async def products_button(num):
    button = InlineKeyboardMarkup(row_width=2)
    products = await products_by_category_id(num)
    for product in products:
        button.insert(
            InlineKeyboardButton(
                text=product["product_name"], callback_data=f"product_{product['id']}"))
    button.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="nazad_2"))

    return button


async def one_product_button(num):
    button = InlineKeyboardMarkup(row_width=3)
    data = await get_product_by_id(num)
    for i in range(1, 10):
        button.insert(
            InlineKeyboardButton(text=pretty_numbers(
                i), callback_data=f"quantity_{i}/{num}"))
    button.add(InlineKeyboardButton(
        text="⬅️ Назад", callback_data=f'nazad_{data["category_id"]}'))
    return button


async def basket_button(tg_id):
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="nazad"),
                InlineKeyboardButton(
                    text="🚖 Оформить заказ", callback_data="order")
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Очистить корзину", callback_data="empty"),
                InlineKeyboardButton(
                    text="⏳ Время доставки", callback_data="eta")

            ]
        ], row_width=1
    )
    products = await get_basket(tg_id)
    basket_text = ""
    price = 0

    for product in products:
        food = await get_product_by_id(product["product_id"])
        basket_text += f'{pretty_numbers(product["product_count"])} ✖️ {food["product_name"]}\n'
        price += product["product_count"]*food["product_price"]
        button.add(
            InlineKeyboardButton(
                text=f'❌ {food["product_name"]}', callback_data=f'empty_{food["id"]}')
        )
    price_text = f"*Товары:* {price:,} сум\n*Доставка:* 10,000 сум\n*Итого:* {price+10000:,} сум"
    return {'basket_text': basket_text, 'price_text': price_text,
            'button': button, 'is_empty': price < 300}


async def payment_methods():
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Наличные", callback_data="pay_Наличные")
            ],
            [
                InlineKeyboardButton(text="Click", callback_data="pay_Click")
            ],
            [
                InlineKeyboardButton(text="Payme", callback_data="pay_Payme")
            ]
        ]
    )
    return button


async def count_button(num):
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="-", callback_data="num_decr"),
                InlineKeyboardButton(text=num, callback_data="num_finish"),
                InlineKeyboardButton(text="+", callback_data="num_incr")
            ]
        ]
    )
    button.add(InlineKeyboardButton(
        text="📥 Добавить в корзину", callback_data="num_add"))
    return button
