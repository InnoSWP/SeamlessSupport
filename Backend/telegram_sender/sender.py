import logging
from os import getenv

import dotenv
from telebot import TeleBot
from telebot import types


# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    # filename="logs.log"
)


# Initialize environment variables from .env file (if it exists)
dotenv.load_dotenv(dotenv.find_dotenv())
BOT_TOKEN = getenv('BOT_TOKEN')
CHANNEL_ID = getenv('CHANNEL_ID')


# Check that critical variables are defined
if BOT_TOKEN is None:
    logging.critical('No BOT_TOKEN variable found in project environment')
if CHANNEL_ID is None:
    logging.critical('No CHANNEL_ID variable found in project environment')


def send_question(question_test: str) -> int:
    bot = TeleBot(BOT_TOKEN)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('✅ Answer the question', callback_data='answerQuestion'))
    message = bot.send_message(CHANNEL_ID, f'New question\n\n{question_test}', reply_markup=markup)

    return message.message_id


def send_dialogue_message(question: str, volunteer_id: int, channel_message_id: int):
    bot = TeleBot(BOT_TOKEN)
    chat = bot.get_chat(volunteer_id)

    pinned_message: types.Message = chat.pinned_message
    if pinned_message.reply_markup is not None:
        json_message = pinned_message.json
        current_channel_message_id = int(json_message['reply_markup']['inline_keyboard'][0][0]['callback_data'].split('/')[1])
        if channel_message_id == current_channel_message_id:  # If user is in current dialogue
            bot.edit_message_text(
                chat_id=volunteer_id,
                message_id=pinned_message.message_id,
                text=pinned_message.text + '\n>> 👤 ' + question,
                reply_markup=pinned_message.reply_markup
            )
        else:  # If user is in different dialogue
            new_reply_markup = types.InlineKeyboardMarkup()
            for [button] in json_message['reply_markup']['inline_keyboard']:
                if button['callback_data'].startswith('new/'):
                    continue
                new_reply_markup.add(types.InlineKeyboardButton(**button))

            last_button = json_message['reply_markup']['inline_keyboard'][-1][0]
            messages = (int(last_button['callback_data'].split('/')[1])
                        if last_button['callback_data'].startswith('new/') else
                        0) + 1
            new_reply_markup.add(
                types.InlineKeyboardButton(callback_data=f'new/{messages}', text=f'📩 New messages: {messages}'))
            bot.edit_message_reply_markup(
                chat_id=volunteer_id,
                message_id=pinned_message.message_id,
                reply_markup=new_reply_markup
            )
