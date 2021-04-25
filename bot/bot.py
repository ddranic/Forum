from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

menu = ReplyKeyboardMarkup(resize_keyboard=True)
but1 = KeyboardButton("О нас")
but2 = KeyboardButton("Правила 📋")
menu.add(but1, but2)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(message.from_user.id, f"Привет, <b>{message.from_user.first_name}!</b>\n"
                                                 f"Я бот форума <b>MRM</b>. Можешь звать меня <b>CMR</b>.\n"
                                                 f"Чем могу помочь?",
                           parse_mode=ParseMode.HTML, reply_markup=menu)


@dp.message_handler()
async def text_handler(message: types.Message):
    if message.text == "О нас":
        await bot.send_message(message.from_user.id, f"Кто <b>мы?</b>:\n\n"
                                                     f"Общедоступная платформа <b>MRM</b>, <i>основанна в 2021 году</i>.\n"
                                                     f"MRM - форум, чтобы:\n"
                                                     f"  ▪️<i>делиться своими историями</i>\n"
                                                     f"  ▪️<i>изучать что-то новое</i>\n"
                                                     f"  ▪️<i>задавать вопросы</i>",
                               parse_mode=ParseMode.HTML)
    elif message.text == "Правила 📋":
        await bot.send_message(message.from_user.id, f"Правила <b>MRM</b> 📋:\n"
                                                     f"  ▪️<i>контент 18+ запрещён</i>\n"
                                                     f"  ▪️<i>повторение тем запрещенно</i>\n"
                                                     f"  ▪️<i>флуд запрещён</i>\n"
                                                     f"  ▪️<i>перед соданием темы, следует убедиться, что такой ещё нет.</i>\n",
                               parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    executor.start_polling(dp)
