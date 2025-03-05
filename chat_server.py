from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    # Render chat interface
    return render_template('chat.html')


@socketio.on('connect')
def handle_connect():
    emit('message', {'agent': 'System',
         'message': 'Connected to chat server.'})


@socketio.on('agent_message')
def handle_agent_message(data):
    # Expected data: {'agent': agent_name, 'message': message_content}
    # Broadcast the agent's message to all connected clients
    emit('message', data, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
