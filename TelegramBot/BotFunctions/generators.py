from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_inline_markup(*args) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in args:
        keyboard.add(InlineKeyboardButton(**button))
    return keyboard

