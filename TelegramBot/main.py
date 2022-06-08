import logging
import asyncio
from os import getenv
from datetime import datetime, timedelta

import dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.types.chat_member_updated import ChatMemberUpdated
import aiogram.utils.exceptions as exceptions

from BotFunctions import filters
from BotFunctions import generators


# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="logs.log"
)


# Initialize environment variables from .env file (if it exists)
dotenv.load_dotenv(dotenv.find_dotenv())
BOT_TOKEN = getenv('BOT_TOKEN')
CHANNEL_ID = getenv("CHANNEL_ID")


# Check that critical variables are defined
if BOT_TOKEN is None:
    logging.critical('No BOT_TOKEN variable found in project environment')
if CHANNEL_ID is None:
    logging.critical('No CHANNEL_ID variable found in project environment')


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer(
        "Hello! I am volunteer helper bot. "
        "My goal is to help managing open (non-answered) questions.\n"
        "To begin, join volunteer's chat and choose any question to answer"
    )


@dp.my_chat_member_handler(filters.is_new_channel_member)
async def new_member_bot(member: ChatMemberUpdated):
    channel_id = member.chat.id
    if member.new_chat_member.user.id == bot.id:
        message = await bot.send_message(
            channel_id,
            f"Hello, I am volunteer management bot! "
            f"To finish configuration please add environment variable:\n"
            f"`CHANNEL_ID={channel_id}`",
            parse_mode='Markdown'
        )
        await bot.edit_message_reply_markup(
            channel_id,
            message.message_id,
            reply_markup=generators.generate_inline_markup({"text": "Delete this message", "callback_data": f"deleteMessage"})
        )


@dp.callback_query_handler(lambda c: c.data == 'deleteMessage')
async def delete_message(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    await bot.delete_message(chat_id, message_id)


# TODO: DELETE
@dp.message_handler(commands=['ask'])
async def send_question(message: Message):
    question_id = message.message_id
    text = f'Question #{question_id}\n\n{message.text.lstrip("/ask ")}'
    markup = generators.generate_inline_markup({
        'text': '✅ Answer the question',
        'callback_data': 'answerQuestion'
    })
    await bot.send_message(CHANNEL_ID, text, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'answerQuestion')
async def answer_question(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    question_text = callback_query.message.text
    question_text = question_text[question_text.find('\n'):].strip()

    try:
        user_markup = generators.generate_inline_markup({'text': '❌ Cancel', 'callback_data': f'cancelAnswer,{message_id}'})
        await bot.send_message(
            user_id,
            f'Please provide answer to the question bellow:\n\n{question_text}',
            reply_markup=user_markup
        )
    except (exceptions.CantInitiateConversation, exceptions.BotBlocked) as e:
        url = f't.me/{(await bot.get_me()).username}?start=start'
        await callback_query.answer('Please start conversation with a bot', url=url)
    else:
        channel_markup = generators.generate_inline_markup({'text': '⌛ In progress', 'callback_data': 'inProgress'})
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=channel_markup)


@dp.callback_query_handler(lambda c: c.data.startswith('cancelAnswer'))
async def cancel_answer(callback_query: CallbackQuery):
    channel_message_id = int(callback_query.data.split(',')[1])
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    markup = generators.generate_inline_markup({'text': '✅ Answer the question', 'callback_data': 'answerQuestion'})
    await bot.edit_message_reply_markup(CHANNEL_ID, channel_message_id, reply_markup=markup)
    await bot.edit_message_text('Answer canceled successfully', user_id, message_id)


@dp.callback_query_handler(lambda c: c.data == 'inProgress')
async def cancel_answer(callback_query: CallbackQuery):
    await callback_query.answer('Question is already taken')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
