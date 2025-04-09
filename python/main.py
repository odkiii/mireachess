import logging
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types.web_app_info import WebAppInfo
import keyboard
import CONFIG
import requests

API_TOKEN = CONFIG.API_TOKEN
DATABASE_URL = CONFIG.DATABASE_URL  # Замените на ваши данные

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
    await save_user(message)  # Передаем message вместо telegram_id
    
    # Получаем информацию о пользователе
    async with db_pool.acquire() as connection:
        user_info = await connection.fetchrow(
            'SELECT username FROM users WHERE telegram_id = $1', 
            telegram_id
        )
    
    # Получаем последнюю сессию
    last_session = await get_last_game_session(telegram_id)
    
    if last_session:
        welcome_text = (
            f"Привет, {user_info['username']}! "
            f"У вас есть незавершенная игра. Хотите продолжить?"
        )
        # Здесь можно добавить кнопку для продолжения игры
        # -------------------------------------------------
        # -------------------------------------------------
        # -------------------------------------------------
        # -------------------------------------------------
        # -------------------------------------------------
        # -------------------------------------------------

    else:
        welcome_text = f"Привет, {user_info['username']}! Давайте начнем новую игру."
    
    await message.answer(welcome_text, reply_markup=keyboard.keyboard1)


# Функция для сохранения пользователя в базе данных
async def save_user(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username  # Получаем никнейм пользователя
    async with db_pool.acquire() as connection:
        await connection.execute('''
            INSERT INTO users (telegram_id, username) 
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET username = EXCLUDED.username
        ''', telegram_id, username)

# получение последней игровой сессии пользователя
async def get_last_game_session(telegram_id: int):
    async with db_pool.acquire() as connection:
        return await connection.fetchrow('''
            SELECT fen
            FROM game_sessions 
            WHERE telegram_id = $1 
            ORDER BY last_updated DESC 
            LIMIT 1
        ''', telegram_id)

# Запуск бота
async def main():
    global db_pool
    db_pool = await create_db_pool()  # Создаем пул соединений с БД
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())