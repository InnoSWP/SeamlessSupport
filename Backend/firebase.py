from os import getenv
from random import choice
from hashlib import sha3_256

import firebase_admin
from firebase_admin import db
from collections import OrderedDict
import dotenv

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


def add_question(question: str, channel_message_id: int, user_email: str) -> None:
    ref = db.reference('/questions')
    ref_child = ref.child(f'{channel_message_id}')
    ref_child.set(
        {
            "channel_message_id": channel_message_id,
            "user_email": user_email,
            "question": question,
            "volunteer_id": 0,
            "answer": ""
        }
    )


def get_user(email: str) -> tuple or None:
    ref = db.reference('/users')
    res: OrderedDict = ref.order_by_child('email').equal_to(email).limit_to_first(1).get()
    return res.popitem() if res else None


def get_volunteer_questions(volunteer_id: int):
    ref = db.reference('/questions/open')
    res: OrderedDict = ref.order_by_child('volunteer_id').equal_to(volunteer_id).get()
    return list(res.values())


def get_user_email(channel_message_id: int):
    ref = db.reference(f'/questions/{channel_message_id}')
    res: dict = ref.get()
    return res.get('email') if type(res) == dict else None


def volunteer_accepted(channel_message_id: int, user_message_id: int, volunteer_id: int) -> None:
    ref = db.reference('/questions/open')
    ref_child = ref.push()
    ref_child.set(
        {
            'volunteer_id': volunteer_id,
            'user_message_id': user_message_id,
            'channel_message_id': channel_message_id
        }
    )


def volunteer_declined(volunteer_id: int) -> None:
    ref = db.reference(f'/questions/open/{volunteer_id}')
    ref.delete()


def volunteer_answered(volunteer_id: int, answer: str) -> None:
    ref = db.reference(f'/questions/open/{volunteer_id}')
    res: dict = ref.get()

    ref = db.reference(f'/questions/{res["channel_message_id"]}')
    ref.update(
        {
            "volunteer_id": volunteer_id,
            "answer": answer
        }
    )

    volunteer_declined(volunteer_id)



