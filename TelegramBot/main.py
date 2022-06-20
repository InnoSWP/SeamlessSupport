import logging
from os import getenv

import dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery
from aiogram.types.chat_member_updated import ChatMemberUpdated
import aiogram.utils.exceptions as exceptions
import requests

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
    """
    Start handler to help new volunteers understand bot
    """

    await message.answer(
        "Hello! I am volunteer helper bot. "
        "My goal is to help managing open (non-answered) questions.\n"
        "To begin, join volunteer's chat and choose any question to answer"
    )


@dp.message_handler(filters.is_private_chat)
async def volunteer_answer(message: Message):
    """
    Send answer to frontend if volunteer have open question that is not yet answered
      > If volunteer have no open questions, just ignore that message
    """

    user_id = message.from_user.id
    answer = message.text
    json = requests.get(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}').json()
    if len(json) == 1:  # If there is exactly 1 open question
        channel_message_id = json[0]['channel_message_id']
        user_message_id = json[0]['user_message_id']
        json = {
            'volunteer_id': user_id,
            'channel_message_id': channel_message_id,
            'answer': answer
        }
        requests.post(f'http://127.0.0.1:5000/answer', json=json)
        await bot.edit_message_text("Your answer saved!", user_id, user_message_id)
        await bot.send_message(user_id, "Thanks for your contribution!\nWe appreciate your work💕")
        await bot.delete_message(CHANNEL_ID, channel_message_id)


@dp.my_chat_member_handler(filters.is_new_channel_member)
async def new_member_bot(member: ChatMemberUpdated):
    """
    Detects when new member joins to channel
      > If new member is THIS bot, sends final configuration message with `delete` button
    """

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
    """
    If message has `delete` inline button which was pressed, delete that message
    """

    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    await bot.delete_message(chat_id, message_id)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data == 'answerQuestion')
async def answer_question(callback_query: CallbackQuery):
    """
    Send to volunteer question that should be answered
      > When volunteer didn't start conversation with a bot, open's link to start chat
      > When volunteer have started conversation, sends question
    """

    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    question_text = callback_query.message.text
    question_text = question_text[question_text.find('\n'):].strip()

    json = requests.get(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}').json()
    if len(json) != 0:  # If volunteer already took some question
        await callback_query.answer('Please answer your taken question first', show_alert=True)
        return

    try:
        user_markup = generators.generate_inline_markup({'text': '❌ Cancel', 'callback_data': f'cancelAnswer,{message_id}'})
        user_message = await bot.send_message(
            user_id,
            f'Please provide answer to the question bellow:\n\n{question_text}',
            reply_markup=user_markup
        )
        volunteer_json = {
            'channel_message_id': message_id,
            'user_message_id': user_message.message_id
        }
        requests.post(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}', json=volunteer_json)
    except (exceptions.CantInitiateConversation, exceptions.BotBlocked) as e:  # If user didn't start conversation
        url = f't.me/{(await bot.get_me()).username}?start=start'
        await callback_query.answer('Please start conversation with a bot', url=url)
    else:  # If everything went ok, change message in channel
        channel_markup = generators.generate_inline_markup({'text': '⌛ In progress', 'callback_data': 'inProgress'})
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=channel_markup)


@dp.callback_query_handler(lambda c: c.data.startswith('cancelAnswer'))
async def cancel_answer(callback_query: CallbackQuery):
    """
    Cancel message when volunteer do not want to answer it anymore
    """

    channel_message_id = int(callback_query.data.split(',')[1])
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    markup = generators.generate_inline_markup({'text': '✅ Answer the question', 'callback_data': 'answerQuestion'})
    await bot.edit_message_reply_markup(CHANNEL_ID, channel_message_id, reply_markup=markup)
    await bot.edit_message_text('Answer canceled successfully', user_id, message_id)
    requests.delete(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}')


@dp.callback_query_handler(lambda c: c.data == 'inProgress')
async def cancel_answer(callback_query: CallbackQuery):
    """
    If message already taken, send 'alert'
    """

    await callback_query.answer('Question is already taken')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
