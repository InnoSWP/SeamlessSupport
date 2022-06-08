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


def send_question(question_test: str) -> None:
    bot = TeleBot(BOT_TOKEN)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('✅ Answer the question', callback_data='answerQuestion'))
    bot.send_message(CHANNEL_ID, f'Question #1\n\n{question_test}', reply_markup=markup)

    bot.close()
