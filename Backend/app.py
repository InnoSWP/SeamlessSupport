from datetime import timedelta


from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
from flask_restful import Api, reqparse
from flask_session import Session
import dotenv

from os import getenv

import resources
import firebase

dotenv.load_dotenv(dotenv.find_dotenv())

app = Flask(__name__)
app.debug = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['transports'] = 'websocket'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

cors = CORS(app)
api = Api(app)
Session(app)

socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/support', methods=['GET'])
def support():
    return render_template('support.html')


@app.route('/answer', methods=['POST'])
def send():
    parser = reqparse.RequestParser()
    parser.add_argument('answer', required=True)
    parser.add_argument('channel_message_id', required=True, type=int)
    args = parser.parse_args()

    user_id = firebase.get_user_id_by_channel_message_id(args['channel_message_id'])

    room = user_id
    socketio.emit(
        'message', {'msg': '  Supporter: ' + args['answer']},
        room=room,
        namespace='/chat'
    )
    return {}


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        email = request.form['email']

        user_id = firebase.get_user_id_by_email(email)
        if user_id is None:
            firebase.add_user(email)

        # Store the data in session
        session['email'] = email
        session['room'] = firebase.get_user_id_by_email(email)
        return render_template('chat.html', session=session)
    else:
        if session.get('room') is not None:
            return render_template('chat.html', session=session)
        else:
            return redirect(url_for('index'))


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': f'  Welcome in our Support Chat'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    answer = firebase.get_automated_answer(message['msg'])
    if answer:
        emit('message', {'msg': "  You" + ': ' + message['msg']}, room=room)
        emit('message', {'msg': "  Supporter: " + ': ' + answer}, room=room)
    else:
        firebase.send_user_message(room, message['msg'])
        emit('message', {'msg': "  You" + ': ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    leave_room(room)
    session.clear()
    emit('status', {'msg': ' has left the room.'}, room=room)


# common access
api.add_resource(resources.CreateUser, '/api/v1/users')  # post
api.add_resource(resources.Users, '/api/v1/users/<string:user_id>')  # get
api.add_resource(resources.UserDialogues, '/api/v1/users/<string:user_id>/dialogues')  # get, delete
api.add_resource(resources.Volunteer, '/api/v1/volunteers/<int:volunteer_id>')  # get
api.add_resource(resources.VolunteerAccepted, '/api/v1/volunteers/<int:volunteer_id>/accepted/<int:channel_message_id>')  # post
api.add_resource(resources.VolunteerDeclined, '/api/v1/volunteers/<int:volunteer_id>/declined/<int:channel_message_id>')  # post
api.add_resource(resources.VolunteerClosed, '/api/v1/volunteers/<int:volunteer_id>/closed/<int:channel_message_id>')  # post
api.add_resource(resources.FrequentQuestions, '/api/v1/frequent-questions/<int:channel_message_id>')  # get
api.add_resource(resources.Dialogue, '/api/v1/dialogues')  # post, get

socketio.run(app, host='10.90.138.120', port='5000')
