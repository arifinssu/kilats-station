from flask import (Flask, Response, jsonify, request)
from flask_socketio import (SocketIO, emit)
from engineio.async_drivers import threading

from .errors import errors

app = Flask(__name__)
app.register_blueprint(errors)
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

@app.route("/")
def index():
    return Response("Hello, world!", status=200)

@app.route("/custom", methods=["POST"])
def custom():
    payload = request.get_json()

    if payload.get("say_hello") is True:
        output = jsonify({"message": "Hello!"})
    else:
        output = jsonify({"message": "..."})

    return output

@app.route("/health")
def health():
    return Response("OK", status=200)

def send_socket(name, data):
    socketio.emit(
        name,
        data,
        namespace='/',
        broadcast=True)

def run(h, p):
    return socketio.run(
        app,
        host=h,
        port=p,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True)

# from lib import gateway
# print(gateway.config)