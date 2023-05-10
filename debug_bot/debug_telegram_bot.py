import asyncio
import emoji
from telebot import TeleBot
from telebot import types
import re

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.async_db import asyncHandler

bot = TeleBot('6269654129:AAHAw3qqV6dJsEB5woAqaKlMzceOUxUikOo')


def split_list(lst: list, n: int):
    if n <= 0:
        return None
    result = []
    i = 0
    while i < len(lst):
        result.append(lst[i:i + n])
        i += n
    return result


def product_page(product_id: int, user_id: int):
    h = asyncHandler()
    product = asyncio.run(h.get_product_by_id(product_id))
    answer = product['name'] + "\n"
    answer += product['description'] + "\n"
    answer += product['photo'] + "\n"
    keyboard = InlineKeyboardMarkup()
    like = InlineKeyboardButton(text="👍", callback_data=f"rate_product_{product['id']}_True")
    dislike = InlineKeyboardButton(text="👎", callback_data=f"rate_product_{product['id']}_False")
    keyboard.add(dislike, like)
    bot.send_message(user_id, answer, reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def start(message):
    h = asyncHandler()
    asyncio.run(h.add_user(str(message.from_user.id), "telegram"))
    answer = "/random - Случайный товар\n"
    answer += "/search <название товара> - Поиск товара\n"
    answer += "/get_recommendation - Получить рекомендацию\n"
    bot.send_message(message.from_user.id, answer)


@bot.message_handler(commands=['random'])
def decorate_info(message):
    h = asyncHandler()
    product = asyncio.run(h.get_random_product())
    answer = product['name'] + "\n"
    answer += product['description'] + "\n"
    answer += product['photo'] + "\n"
    bot.send_message(message.from_user.id, answer)


@bot.message_handler(commands=['search'])
def decorate_info(message):
    command = re.split(r' ', message.text, 1)
    h = asyncHandler()
    products = asyncio.run(h.get_product_by_req(command[1]))
    if products is None:
        bot.send_message(message.from_user.id, "Товар не найден")
        return
    else:
        num = 0
        keyboard = InlineKeyboardMarkup()
        buttons = []
        for i in products:
            num += 1
            answer = str(num) + "\n"
            buttons.append(InlineKeyboardButton(text=str(num), callback_data=f"get_product_{i['id']}"))
            answer += i['name'] + "\n"
            answer += i['description'] + "\n"
            answer += i['photo'] + "\n"
            bot.send_message(message.from_user.id, answer)

        buttons = split_list(buttons, 3)
        for i in buttons:
            keyboard.add(*i)
        bot.send_message(message.from_user.id, "Какой именно фильм?", reply_markup=keyboard)


@bot.message_handler(commands=['get_recommendation'])
def get_recommendation(message):
    h = asyncHandler()
    user = asyncio.run(h.get_user(str(message.from_user.id), "telegram"))
    product = asyncio.run(h.get_recommend_cat(user['id']))
    for i in product:
        product_page(i['id'], message.from_user.id)


@bot.callback_query_handler(func=lambda c: True)
def handle_query(call: types.CallbackQuery):
    if call.message:
        if call.data.startswith('get_product_'):
            product_id = call.data.split('_')[2]
            product_page(int(product_id), call.message.chat.id)

        elif call.data.startswith('rate_product_'):
            product_id = call.data.split('_')[2]
            rate = call.data.split('_')[3]
            rate = True if rate == "True" else False
            h = asyncHandler()
            user = asyncio.run(h.get_user(str(call.from_user.id), "telegram"))
            asyncio.run(h.rate_product(int(user['id']), int(product_id), rate))
            bot.send_message(call.message.chat.id, "Спасибо за оценку")


if __name__ == "__main__":
    bot.infinity_polling()
