from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup,KeyboardButton

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💎 Premium',callback_data='premium'),InlineKeyboardButton(text="🔪 Оружие",callback_data='guns')],
    [InlineKeyboardButton(text='👤 Профиль',callback_data='profile')]

])
payment = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплатить ⭐', pay=True)]
])
