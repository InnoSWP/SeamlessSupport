from flask import jsonify
from flask_restful import Resource, reqparse, abort

import firebase
from telegram_sender import sender


class Users(Resource):
    def get(self, email):
        user_id, data = firebase.get_user(email)
        return data

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        args = parser.parse_args()

        firebase.add_user(args['email'])
        return {}
        # TODO: somehow send email or authorise


class Question(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('question', required=True)
        parser.add_argument('user_email', required=True)
        args = parser.parse_args()
        message_id = sender.send_question(args['question'])
        firebase.add_question(question=args['question'], channel_message_id=message_id, user_email=args['user_email'])
        return {}


class Volunteer(Resource):
    def post(self, volunteer_id: int):
        parser = reqparse.RequestParser()
        parser.add_argument('channel_message_id', required=True, type=int)
        parser.add_argument('user_message_id', required=True, type=int)
        args = parser.parse_args()

        firebase.volunteer_accepted(
            channel_message_id=args['channel_message_id'],
            user_message_id=args['user_message_id'],
            volunteer_id=volunteer_id
        )
        return {}

    def get(self, volunteer_id: int):
        return firebase.get_volunteer_questions(volunteer_id=volunteer_id)

    def delete(self, volunteer_id: int):
        firebase.volunteer_declined(volunteer_id)
        return {}
