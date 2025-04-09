from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

button = InlineKeyboardButton(
    text='Играть',
    web_app=WebAppInfo(url='https://infallibly-refined-shark.cloudpub.ru/'))

keyboard1 = InlineKeyboardMarkup(
    inline_keyboard=[[button]]
)