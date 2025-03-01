import logging
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types.web_app_info import WebAppInfo
import keyboard
import requests

API_TOKEN = '8195958390:AAGVlDEGu4IRova7wXPB_6EgsKuG_pkBbek'
DATABASE_URL = 'postgresql://postgres:12345678@localhost:5432/mireachessdb'  # Замените на ваши данные

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для подключения к базе данных
async def create_db_pool():
    try:
        return await asyncpg.create_pool(DATABASE_URL)
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        raise



# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    telegram_id = message.from_user.id
    await save_user(telegram_id)

    print(f'Получено айди {telegram_id}')
    await message.answer(f"Привет! Ваш id - {telegram_id}", reply_markup=keyboard.keyboard1)  # Передаем клавиатуру в ответ

# Функция для сохранения пользователя в базе данных
async def save_user(telegram_id: int):
    async with db_pool.acquire() as connection:
        await connection.execute('''
            INSERT INTO users (telegram_id) VALUES ($1)
            ON CONFLICT (telegram_id) DO NOTHING
        ''', telegram_id)

# Запуск бота
async def main():
    global db_pool
    db_pool = await create_db_pool()  # Создаем пул соединений с БД
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

