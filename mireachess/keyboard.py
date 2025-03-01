from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

button = InlineKeyboardButton(
    text='Играть',
    web_app=WebAppInfo(url='https://mireachess.netlify.app/'))

keyboard1 = InlineKeyboardMarkup(
    inline_keyboard=[[button]]
)