from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from api import *

start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🍴 Меню")
        ],
        [
            KeyboardButton(text="🛍 Мои заказы"),
            KeyboardButton(text="✍️ Оставить отзыв")
        ]
    ], resize_keyboard=True
)

phone_number = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Мой номер", request_contact=True)
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ],
    ], resize_keyboard=True
)

location = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📍 Отправить геолокацию",
                           request_location=True)
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ], resize_keyboard=True
)

nazad = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ], resize_keyboard=True
)

# menu = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="🗺 Мои адреса")
#         ],
#         [
#             KeyboardButton(text="📍 Отправить геолокацию"),
#             KeyboardButton(text="⬅️ Назад")
#         ]
#     ], resize_keyboard=True
# )


async def categories(tg_id):
    button = ReplyKeyboardMarkup(row_width=2)
    categories = await all_categories()
    basket = await get_basket(tg_id)

    if basket:
        button.add(
            KeyboardButton(text="📥 Корзина"))
        button.add(
            KeyboardButton(text=categories[0]["category_name"]))
        for category in categories[1:]:
            button.insert(
                KeyboardButton(text=category["category_name"])
            )
    else:
        for category in categories:
            button.insert(
                KeyboardButton(text=category["category_name"])
            )
        button.add(
            KeyboardButton(text="📥 Корзина"))

    button.insert(
        KeyboardButton(text="⬅️ Назад")
    )

    return button


async def products(category_name, tg_id):
    button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    products = await products_by_category_name(category_name)
    basket = await get_basket(tg_id)
    if basket:
        button.add(
            KeyboardButton(text="📥 Корзина"))
        button.add(
            KeyboardButton(text=products[0]["product_name"]))
        for product in products[1:]:
            button.insert(
                KeyboardButton(
                    text=product["product_name"]))
    else:
        for product in products:
            button.insert(
                KeyboardButton(
                    text=product["product_name"]))
    button.add(
        KeyboardButton(text="⬅️ Назад"))

    return button

product = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📥 Корзина")
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ], resize_keyboard=True
)

payment_method = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Наличные")
        ],
        [
            KeyboardButton(text="Click")
        ],
        [
            KeyboardButton(text="Payme")
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ],
    ], resize_keyboard=True
)

confirm = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Подтвердить")
        ],
        [
            KeyboardButton(text="❌ Отменить")
        ]
    ], resize_keyboard=True
)
