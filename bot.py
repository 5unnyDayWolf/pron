from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import sqlite3

API_TOKEN = '5617293957:AAGg0LteP5V2kYapOZ-0_RVyjtmH10kk7No' # Токен 
logging.basicConfig(level=logging.INFO) # Initialize bot and dispatcher
proxy = 'http://vidproxy.com/'
bot = Bot(token=API_TOKEN, proxy=proxy)
dp = Dispatcher(bot)

conn = sqlite3.connect('db.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER, block INTEGER);""")
conn.commit()

ADMIN = '1966314752'

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Рассылка"))
kb.add(types.InlineKeyboardButton(text="Статистика"))

class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()

@dp.message_handler(commands=['start'])
async def start(message: Message):
  cur = conn.cursor()
  cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
  result = cur.fetchone()
  if message.from_user.id == ADMIN:
    await message.answer('Здарова босс! Держите клавиатуру к вашим услугам)', reply_markup=kb)
  else:
      if result is None:
        cur = conn.cursor()
        cur.execute(f'''SELECT * FROM users WHERE (user_id="{message.from_user.id}")''')
        entry = cur.fetchone()
        if entry is None:
          cur.execute(f'''INSERT INTO users VALUES ('{message.from_user.id}', '0')''')
          conn.commit()
          await message.answer('Выберите тариф подходящий для вас!)')
      else:
        await message.answer('Ты был заблокирован!')

@dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: Message):
  await dialog.spam.set()
  await message.answer('Напиши текст рассылки')

@dp.message_handler(state=dialog.spam)
async def start_spam(message: Message, state: FSMContext):
  if message.text == 'Назад':
    await message.answer('Главное меню', reply_markup=kb)
    await state.finish()
  else:
    cur = conn.cursor()
    cur.execute(f'''SELECT user_id FROM users''')
    spam_base = cur.fetchall()
    for z in range(len(spam_base)):
        await bot.send_message(spam_base[z][0], message.text)
        await message.answer('Рассылка завершена', reply_markup=kb)
        await state.finish()

@dp.message_handler(content_types=['text'], text='Статистика')
async def hfandler(message: types.Message, state: FSMContext):
  cur = conn.cursor()
  cur.execute('''select * from users''')
  results = cur.fetchall()
  await message.answer(f'Людей которые когда либо заходили в бота: {len(results)}')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
