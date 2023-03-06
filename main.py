import json
from chatgpt_api import Chatbot
from flask import Flask, render_template
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

config_file = 'config.json'

with open(config_file, encoding="utf-8") as f:
    config = json.load(f)

chatbot = Chatbot(config)


@app.route('/')
def sessions():
    return render_template('session.html')


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(input_dict, methods=['GET', 'POST']):
    print('received my event: ' + str(input_dict))

    if 'data' in input_dict:
        return

    user_name = input_dict.get('user_name')
    prompt = input_dict.get('message')
    conversation_id = input_dict.get('conversation_id')

    if not conversation_id:
        conversation_id = None

    socketio.emit('my response', input_dict, callback=messageReceived)
    message = ''

    try:
        response = chatbot.ask(prompt, conversation_id=conversation_id)

        responses = list(response)

        if responses:
            data = responses[-1]
            conversation_id = data['conversation_id']
            message = data["message"]

    except:
        message = 'Inner server exception!'
        app.logger.exception(message)

    # print('chatgpt message:', message)

    input_dict['user_name'] = 'Robot'
    input_dict['message'] = message
    input_dict['conversation_id'] = conversation_id
    socketio.emit('my response', input_dict, callback=messageReceived)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
