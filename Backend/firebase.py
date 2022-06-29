from os import getenv
from random import choice
from hashlib import sha3_256

import firebase_admin
from firebase_admin import db
from collections import OrderedDict
import dotenv

from telegram_sender import sender

dotenv.load_dotenv(dotenv.find_dotenv())

cred_obj = firebase_admin.credentials.Certificate('seamless-support-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(
    cred_obj,
    {
        'databaseURL': getenv('DATABASE_URL')
    }
)


def add_user(email: str) -> None:
    ref = db.reference('/users')
    ref_child = ref.push()
    password = ''.join([choice(getenv('PASSWORD_ALPHABET')) for _ in range(50)])
    ref_child.set(
        {
            'email': email,
            'password': sha3_256((password + getenv('SALT')).encode('UTF-8')).hexdigest()
        }
    )


def get_user(user_id: str) -> dict or None:
    ref = db.reference(f'/users/{user_id}')
    res: OrderedDict = ref.get()
    if res is None:
        return None
    user_id, res_dict = res.popitem()
    res_dict['user_id'] = user_id
    return res_dict


def get_user_dialogue(user_id: str, read_messages: bool = False) -> list[dict]:
    ref = db.reference('/current-dialogues/' + user_id)
    res: OrderedDict = ref.get()
    messages = list(res.values()) if (res is not None) else []
    if read_messages:
        __set_new_messages_counter(user_id, 0)
    return messages


def send_user_message(user_id: str, message: str) -> None:
    message_count = __get_message_count(user_id, is_user=True)
    if message_count == 0:
        __create_frequent_question(user_id, message)
    __send_message(user_id, message, True)
    __set_new_messages_counter(user_id)
    json = __get_frequent_question_by_user_id(user_id)
    if json.get('volunteer_id') is not None:
        sender.send_dialogue_message(message, json['volunteer_id'], json['message_id'])


def send_volunteer_message(channel_message_id: int, volunteer_id: int, message: str) -> None:
    user_id = get_user_id_by_channel_message_id(channel_message_id)
    message_count = __get_message_count(user_id, is_user=False)
    if message_count == 0:
        __answer_frequent_question(channel_message_id, volunteer_id, message)
    __send_message(user_id, message, False)


def close_dialogue(user_id: str, volunteer_id: int, channel_message_id: int) -> None:
    ref_current = db.reference('/current-dialogues/' + user_id)
    ref_closed = db.reference('/closed-dialogues/' + user_id)
    ref_closed.push(ref_current.get())
    ref_current.delete()
    ref_volunteer = db.reference(f'/volunteer/{volunteer_id}/dialogues/{channel_message_id}')
    ref_volunteer.delete()


def user_closed_dialogue(user_id: str):
    json = __get_frequent_question_by_user_id(user_id)
    close_dialogue(user_id, json['volunteer_id'], json['message_id'])


def volunteer_accepted(channel_message_id: int, volunteer_id: int) -> None:
    ref = db.reference(f'/volunteer/{volunteer_id}/dialogues')
    ref.child(str(channel_message_id)).set(
        {
            'user_id': get_user_id_by_channel_message_id(channel_message_id),
            'channel_message_id': channel_message_id
        }
    )
    ref = db.reference(f'/frequent-questions/{channel_message_id}')
    ref.update(
        {
            'volunteer_id': volunteer_id
        }
    )


def volunteer_declined(channel_message_id: int, volunteer_id: int) -> None:
    ref = db.reference(f'/volunteer/{volunteer_id}/dialogues/{channel_message_id}')
    ref.delete()
    ref = db.reference(f'/frequent-questions/{channel_message_id}')
    ref.update(
        {
            'volunteer_id': None
        }
    )


def get_volunteer_dialogues(volunteer_id: int) -> list[dict]:
    ref = db.reference(f'/volunteer/{volunteer_id}/dialogues')
    res: OrderedDict = ref.get()
    return list(res.values())


def get_frequent_message(channel_message_id: int):
    ref = db.reference(f'/frequent-questions/{channel_message_id}')
    return ref.get()


def __send_message(user_id: str, message: str, is_user: bool) -> None:
    ref = db.reference('/current-dialogues/' + user_id)
    ref_child = ref.push()
    ref_child.set(
        {
            'message': message,
            'is_user': is_user
        }
    )


def __create_frequent_question(user_id: str, message: str) -> None:
    ref = db.reference('/frequent-questions')
    message_id = sender.send_question(message)
    ref.child(str(message_id)).set(
        {
            'user_id': user_id,
            'question': message,
            'message_id': message_id,
            'new_messages': 0
        }
    )


def __answer_frequent_question(channel_message_id: int, volunteer_id: int, message: str) -> None:
    ref = db.reference(f'/frequent-questions/{channel_message_id}')
    ref.update(
        {
            'volunteer_id': volunteer_id,
            'answer': message
        }
    )


def __get_message_count(user_id: str, is_user: bool) -> int:
    res: list = get_user_dialogue(user_id)
    return len(list(filter(lambda d: d['is_user'] == is_user, res))) if (res is not None) else 0


def __set_new_messages_counter(user_id: str, value: int = None):
    json = __get_frequent_question_by_user_id(user_id)
    channel_message_id = json['message_id']
    ref = db.reference(f'/frequent-questions/{channel_message_id}')
    ref.update(
        {
            'new_messages': json['new_messages'] + 1 if (value is None) else 0
        }
    )


def __get_frequent_question_by_user_id(user_id: str) -> dict:
    ref = db.reference('/frequent-questions')
    res: OrderedDict = ref.order_by_child('user_id').equal_to(user_id).limit_to_last(1).get()
    json = res.popitem()[1]
    return json


def get_user_id_by_channel_message_id(channel_message_id: int) -> str or None:
    ref = db.reference(f'/frequent-questions/{channel_message_id}')
    res: OrderedDict = ref.get()
    return res['user_id'] if (res is not None) else None


def get_user_id_by_email(email: str) -> str or None:
    ref = db.reference('/users')
    res: OrderedDict = ref.order_by_child('email').equal_to(email).limit_to_first(1).get()
    return res.popitem()[0] if res else None
