from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests


def generate_inline_markup(*args) -> InlineKeyboardMarkup:
    """
    Generate inline markup by list of dicts with parameters
    """
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in args:
        keyboard.add(InlineKeyboardButton(**button))
    return keyboard


def generate_user_dialogues(user_id: int) -> InlineKeyboardMarkup:
    markup_dict = []
    dialogues: list[dict] = requests.get(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}').json()
    for dialogue in dialogues:
        channel_message_id = dialogue['channel_message_id']
        question = requests.get(f'http://127.0.0.1:5000/api/v1/frequent-questions/{channel_message_id}').json()
        markup_dict.append(
            {
                'text': question['question'],
                'callback_data': f'id/{dialogue["channel_message_id"]}'
            }
        )
    markup_dict.append({'text': '🔄 Reload', 'callback_data': 'reload'})
    return generate_inline_markup(*markup_dict)
