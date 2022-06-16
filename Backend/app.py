from datetime import timedelta
import requests

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from flask_restful import Api, reqparse

import resources
import firebase

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=5)

api = Api(app)
Session(app)

socketio = SocketIO(app, manage_session=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/answer', methods=['POST'])
def send():
    parser = reqparse.RequestParser()
    parser.add_argument('volunteer_id', required=True, type=int)
    parser.add_argument('answer', required=True)
    parser.add_argument('channel_message_id', required=True, type=int)
    args = parser.parse_args()

    user_email = firebase.get_user_email(args['channel_message_id'])
    firebase.volunteer_answered(args['volunteer_id'], args['answer'])

    room = user_email
    socketio.emit(
        'message', {'msg': args['answer']},
        room=room,
        namespace='/chat'
    )
    return {}


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Store the data in session
        session['email'] = email
        session['room'] = email
        return render_template('chat.html', session=session)
    else:
        if session.get('email') is not None:
            return render_template('chat.html', session=session)
        else:
            return redirect(url_for('index'))


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('email') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    question_json = {
        'user_email': session.get('email'),
        'question': message['msg']
    }
    requests.post('http://127.0.0.1:5000/api/v1/question/', json=question_json)

    room = session.get('room')
    emit('message', {'msg': session.get('email') + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    email = session.get('email')
    leave_room(room)
    session.clear()
    emit('status', {'msg': email + ' has left the room.'}, room=room)


# common access
api.add_resource(resources.Users, '/api/v1/users')  # get, post
api.add_resource(resources.Volunteer, '/api/v1/volunteers/<int:volunteer_id>')  # get, post, delete
api.add_resource(resources.Question, '/api/v1/question/')  # post


if __name__ == '__main__':
    socketio.run(app)
