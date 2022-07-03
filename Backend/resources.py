import requests
from flask import jsonify
from flask_restful import Resource, reqparse, abort

import firebase

HOST_PORT = '0.0.0.0:5000'


class CreateUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        args = parser.parse_args()

        firebase.add_user(args['email'])


class Users(Resource):
    def get(self, user_id: str):
        return firebase.get_user(user_id)


class UserDialogues(Resource):
    def get(self, user_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('read_messages', required=False, default=False, type=bool)
        args = parser.parse_args()
        return firebase.get_user_dialogue(user_id, args['read_messages'])

    def delete(self, user_id: str):
        firebase.user_closed_dialogue(user_id=user_id)


class Dialogue(Resource):
    def post(self) -> None:
        parser = reqparse.RequestParser()
        parser.add_argument('message', required=True)
        parser.add_argument('is_user', required=True, type=bool)
        parser.add_argument('user_id', required=False)
        parser.add_argument('volunteer_id', required=False, type=int)
        parser.add_argument('channel_message_id', required=False, type=int)
        args = parser.parse_args()

        if args['is_user']:
            assert args.get('user_id') is not None
            firebase.send_user_message(args['user_id'], args['message'])
        else:  # If bot send the request
            assert args.get('volunteer_id') is not None
            assert args.get('channel_message_id') is not None
            firebase.send_volunteer_message(args['channel_message_id'], args['volunteer_id'], args['message'])
            print('ndjnsdkjdskjsdkjdskjdskjdsjk')
            print(f'http://{HOST_PORT}/answer')


class FrequentQuestions(Resource):
    def get(self, channel_message_id: int):
        return firebase.get_frequent_message(channel_message_id)


class Volunteer(Resource):
    def get(self, volunteer_id: int):
        return firebase.get_volunteer_dialogues(volunteer_id=volunteer_id)


class VolunteerAccepted(Resource):
    def post(self, volunteer_id: int, channel_message_id: int):
        firebase.volunteer_accepted(channel_message_id=channel_message_id, volunteer_id=volunteer_id)


class VolunteerDeclined(Resource):
    def post(self, volunteer_id: int, channel_message_id: int):
        firebase.volunteer_declined(channel_message_id=channel_message_id, volunteer_id=volunteer_id)


class VolunteerClosed(Resource):
    def post(self, volunteer_id: int, channel_message_id: int):
        firebase.close_dialogue(
            user_id=firebase.get_user_id_by_channel_message_id(channel_message_id),
            volunteer_id=volunteer_id,
            channel_message_id=channel_message_id
        )
