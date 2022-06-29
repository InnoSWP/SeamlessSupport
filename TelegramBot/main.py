import logging
from os import getenv
from asyncio import sleep

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

# Initialize global variable to store last messages.
# Volatile, but effective as it will simplify code.
storage = dict()


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

    chat_info = await bot.get_chat(user_id)
    pinned_message: Message = chat_info.pinned_message
    if pinned_message.reply_markup is not None:
        channel_message_id = pinned_message.reply_markup.inline_keyboard[0][0]['callback_data'].split('/')[1]
        answer_json = {
            'message': answer,
            'channel_message_id': channel_message_id,
            'volunteer_id': user_id,
            'is_user': False
        }
        requests.post('http://127.0.0.1:5000/api/v1/dialogues', json=answer_json)
        message = await bot.edit_message_text(
            chat_id=user_id,
            message_id=pinned_message.message_id,
            text=pinned_message.text + '\n>> 🧑‍💻 ' + answer,
            reply_markup=pinned_message.reply_markup
        )
        storage[user_id] = message.message_id


@dp.my_chat_member_handler(filters.is_new_channel_member)
async def new_member_bot(member: ChatMemberUpdated):
    """
    Detects when new member joins to channel
      > If new member is THIS bot, sends final configuration message with `delete` button
    """

    channel_id = member.chat.id
    if member.new_chat_member.user.id == bot.id:
        await bot.send_message(
            channel_id,
            f"Hello, I am volunteer management bot! "
            f"To finish configuration please add environment variable:\n"
            f"`CHANNEL_ID={channel_id}`",
            parse_mode='Markdown',
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

    chat = await bot.get_chat(user_id)
    if chat.pinned_message is not None:
        pinned_message: Message = chat.pinned_message
        if pinned_message.from_user.is_bot and pinned_message.reply_markup is not None:
            await callback_query.answer('Please cancel your dialogue first to accept new one', show_alert=True)
            return

    requests.post(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}/accepted/{message_id}')

    try:
        user_markup = generators.generate_inline_markup(
            {'text': '🔄 Reload', 'callback_data': f'relDel/{message_id}'},
            {'text': '❌ Cancel', 'callback_data': f'cancelD/{message_id}'},
        )
        if storage.get(user_id) is None:
            message = await bot.send_message(chat_id=user_id, text=f'⌛ loading ⌛')
            storage[user_id] = message.message_id
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=storage.get(user_id),
            text=f'You accepted new question! Please reload to answer, or click cancel to cancel it.',
            reply_markup=user_markup
        )
    except (exceptions.CantInitiateConversation, exceptions.BotBlocked):  # If user didn't start conversation
        url = f't.me/{(await bot.get_me()).username}?start=start'
        await callback_query.answer('Please start conversation with a bot', url=url)
    else:  # If everything went ok, change message in channel
        channel_markup = generators.generate_inline_markup({'text': '⌛ In progress', 'callback_data': 'inProgress'})
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=channel_markup)


@dp.callback_query_handler(lambda c: c.data.startswith('id/'))
async def send_dialogue(callback_query: CallbackQuery):
    channel_message_id = callback_query.data.split('/')[1]
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    question = requests.get(f'http://127.0.0.1:5000/api/v1/frequent-questions/{channel_message_id}').json()
    dialogue: list[dict] = requests.get(f'http://127.0.0.1:5000/api/v1/users/{question["user_id"]}/dialogues', json={'read_messages': True}).json()
    message_text = 'Your messages are going to be send in current dialogue:\n'
    for message in dialogue:
        icon = '👤' if message['is_user'] else '🧑‍💻'
        text = icon + ' ' + message['message']
        message_text += text + '\n'

    markup = generators.generate_inline_markup(
        {'text': '⬅ Go back', 'callback_data': f'cid/{channel_message_id}'},
        {'text': '🏁 Finish dialogue', 'callback_data': f'fid/{channel_message_id}'}
    )
    message = await bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=message_text,
        reply_markup=markup)
    await bot.pin_chat_message(user_id, message_id)
    storage[user_id] = message.message_id


@dp.callback_query_handler(lambda c: c.data.startswith('cancelD/'))
async def cancel_dialogue(callback_query: CallbackQuery):
    """
    Cancel message when volunteer do not want to answer it anymore
    """

    channel_message_id = int(callback_query.data.split('/')[1])
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    requests.post(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}/declined/{channel_message_id}')

    markup = generators.generate_inline_markup({'text': '✅ Answer the question', 'callback_data': 'answerQuestion'})
    await bot.edit_message_reply_markup(CHANNEL_ID, channel_message_id, reply_markup=markup)
    message = await bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text='You successfully disconnected from dialogue\n\nHere is the list of dialogues that you are currently working on:',
        reply_markup=generators.generate_user_dialogues(user_id))
    storage[user_id] = message


@dp.callback_query_handler(lambda c: c.data.startswith('cid/'))
async def cancel_answer(callback_query: CallbackQuery):
    channel_message_id = callback_query.data.split('/')[1]
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    question = requests.get(f'http://127.0.0.1:5000/api/v1/frequent-questions/{channel_message_id}').json()
    requests.get(f'http://127.0.0.1:5000/api/v1/users/{question["user_id"]}/dialogues', json={'read_messages': True}).json()

    await bot.unpin_all_chat_messages(user_id)
    await sleep(1)  # On some platforms telegram breaks without this break (e.x. Ubuntu 20)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=callback_query.message.text + '\n----- You closed dialogue -----'
    )
    message = await bot.send_message(
        chat_id=user_id,
        text="Here is the list of dialogues that you are currently working on:",
        reply_markup=generators.generate_user_dialogues(user_id)
    )
    storage[user_id] = message.message_id


@dp.callback_query_handler(lambda c: c.data.startswith('fid/'))
async def finish_dialogue(callback_query: CallbackQuery):
    channel_message_id = callback_query.data.split('/')[1]
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    question = requests.get(f'http://127.0.0.1:5000/api/v1/frequent-questions/{channel_message_id}').json()
    dialogue: list[dict] = requests.get(f'http://127.0.0.1:5000/api/v1/users/{question["user_id"]}/dialogues', json={'read_messages': True}).json()
    if all([message['is_user'] for message in dialogue]):
        await callback_query.answer('You should provide at least 1 answer to finish dialogue', show_alert=True)
        return

    requests.post(f'http://127.0.0.1:5000/api/v1/volunteers/{user_id}/closed/{channel_message_id}')
    await bot.unpin_all_chat_messages(user_id)
    await sleep(1)  # On some platforms telegram breaks without break
    await bot.edit_message_text('You successfully finished dialogue', user_id, message_id)
    message = await bot.send_message(
        chat_id=user_id,
        text="Here is the list of dialogues that you are currently working on:",
        reply_markup=generators.generate_user_dialogues(user_id)
    )
    storage[user_id] = message.message_id


@dp.callback_query_handler(lambda c: c.data == 'inProgress')
async def cancel_answer(callback_query: CallbackQuery):
    """
    If message already taken, send 'alert'
    """

    await callback_query.answer('Question is already taken')


@dp.callback_query_handler(lambda c: c.data.startswith('new/'))
async def cancel_answer(callback_query: CallbackQuery):
    """
    If `new messages` counter is pressed, send `cancel please`
    """

    await callback_query.answer('Please cancel or finish your current dialogue first', show_alert=True)


@dp.callback_query_handler(lambda c: c.data.startswith('relDel/'))
async def reload_and_delete_message(callback_query: CallbackQuery):
    channel_message_id = callback_query.data.split('/')[1]
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    await callback_query.answer('Dialogue accepted successfully')
    await bot.delete_message(CHANNEL_ID, int(channel_message_id))
    message = await bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text="Here is the list of dialogues that you are currently working on:",
        reply_markup=generators.generate_user_dialogues(user_id)
    )
    storage[user_id] = message


@dp.callback_query_handler(lambda c: c.data == 'reload')
async def reload_message(callback_query: CallbackQuery):
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    await callback_query.answer('Dialogues reloaded successfully')
    message = await bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text="Here is the list of dialogues that you are currently working on:",
        reply_markup=generators.generate_user_dialogues(user_id)
    )
    storage[user_id] = message


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
