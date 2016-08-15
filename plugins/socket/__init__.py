from threading import Thread
import os
import logging
from flask import Flask, request, redirect
from flask_socketio import SocketIO, emit

from pokemongo_bot import logger
from pokemongo_bot.event_manager import manager

from plugins.socket import myjson
from plugins.socket import botevents
from plugins.socket import uievents

# pylint: disable=unused-variable, unused-argument

@manager.on('bot_setup')
def boot(bot=None):
    if bot is None:
        return

    SOCKET_THREAD = Thread(target=run_socket_server, args=(bot.config.socket_host, bot.config.socket_port,))
    SOCKET_THREAD.daemon = True
    SOCKET_THREAD.start()


def log(text, color="black"):
    logger.log(text, color=color, prefix="Socket")


def run_socket_server(host='0.0.0.0', port=8000):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "OpenPoGoBotSocket"
    socketio = SocketIO(app, logging=False, engineio_logger=False, json=myjson)

    @app.route("/")
    def redirect_online():
        return redirect("http://openpogoui.nicontoso.eu")

    state = {}

    botevents.register_bot_events(socketio, state)
    uievents.register_ui_events(socketio, state)

    socketio.run(app, host=host, port=port, debug=False, use_reloader=False, log_output=False)
    log('Server started on {}:{}'.format(host, port))
