import requests
from aiohttp import ClientSession
from data import config


url = config.URL
head = {"Authorization": f"token {config.MY_TOKEN}"}


async def all_categories():
    async with ClientSession() as sessions:
        http = f"{url}/types/"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def get_category_by_id(category_id):
    async with ClientSession() as sessions:
        http = f"{url}/api/v1/category/{category_id}"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def products_by_category_id(num):
    async with ClientSession() as sessions:
        http = f"{url}/filter/category/id/{num}/"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def get_product_by_id(num):
    async with ClientSession() as sessions:
        http = f"{url}/api/v1/product/{num}"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def purchase_product(tg_id, product_id, count):
    async with ClientSession() as sessions:
        http = f"{url}/upgrade/{tg_id}/{product_id}/"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                async with sessions.put(http, data={
                    "product_count": count
                }, headers=head):
                    return "Обновлено!"

    async with ClientSession() as sessions:
        http = f"{url}/api/v1/basket/"
        async with sessions.post(http, data={
            "telegram_id": tg_id,
            "product_id": product_id,
            "product_count": count
        }, headers=head):
            return "Добавлено!"


async def delete_product(tg_id, product_id):
    async with ClientSession() as sessions:
        http = f"{url}/upgrade/{tg_id}/{product_id}/"
        async with sessions.delete(http, headers=head):
            return "Удалено!"


async def get_basket(tg_id):
    async with ClientSession() as sessions:
        http = f"{url}/filter/basket/{tg_id}/"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def empty_basket(tg_id):
    async with ClientSession() as sessions:
        http = f"{url}/filter/basket/{tg_id}/"
        async with sessions.delete(http, headers=head):
            return "Очищено!"


async def post_user(username, tg_id):
    async with ClientSession() as sessions:
        http = f"{url}/users/{tg_id}/"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()

    async with ClientSession() as sessions:
        http = f"{url}/users/"
        async with sessions.post(http, data={
            "username": username,
            "telegram_id": tg_id
        }, headers=head):
            return "Пользователь добавлен!"


async def put_number(tg_id, number):
    async with ClientSession() as sessions:
        http = f"{url}/users/{tg_id}/"
        async with sessions.put(http, data={
            "phone_number": number
        }, headers=head):
            return "Обновлено"


async def put_location(tg_id, location):
    async with ClientSession() as sessions:
        http = f"{url}/users/{tg_id}/"
        async with sessions.put(http, data={
            "user_address": location
        }, headers=head):
            return "Обновлено"


async def all_orders():
    async with ClientSession() as session:
        http = f"{url}/api/v1/order/"
        async with session.get(http, headers=head) as data:
            return await data.json()


async def get_order_by_user(tg_id):
    async with ClientSession() as session:
        http = f"{url}/orders/{tg_id}"
        async with session.get(http, headers=head) as data:
            return await data.json()


async def post_order(tg_id, products, method, address, sum, status):
    async with ClientSession() as session:
        http = f"{url}/orders/"
        async with session.post(http, data={
            "telegram_id": tg_id,
            "order_items": products,
            "payment_method": method,
            "order_address": address,
            "order_sum": sum,
            "order_status": status
        }, headers=head):
            return "Успешно заказано!"


async def get_category_by_name(category_name):
    async with ClientSession() as sessions:
        http = f"{url}/filter/category/{category_name}/"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def products_by_category_name(category_name):
    async with ClientSession() as sessions:
        http = f"{url}/filter/category/name/{category_name}/"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def get_product_by_name(name):
    async with ClientSession() as sessions:
        http = f"{url}/filter/product/name/{name}"
        async with sessions.get(http, headers=head) as data:
            if data.status == 200:
                return await data.json()


async def comment(tg_id, username, comment):
    async with ClientSession() as session:
        http = f"{url}/comment/"
        async with session.post(http, data={
            "telegram_id": tg_id,
            "username": username,
            "comment": comment
        }, headers=head):
            return "Успешно прокомментиравно!"
