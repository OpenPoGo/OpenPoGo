from threading import Thread
import os
import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit

from pokemongo_bot import logger
from pokemongo_bot.event_manager import manager
from api.json_encodable import JSONEncodable
from api.inventory_parser import InventoryParser
from plugins.socket import myjson

# pylint: disable=unused-variable, unused-argument

logging.getLogger('socketio').disabled = True
logging.getLogger('engineio').disabled = True
logging.getLogger('werkzeug').disabled = True

def run_socket_server():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "OpenPoGoBotSocket"
    socketio = SocketIO(app, logging=False, engineio_logger=False, json=myjson)

    cached_events = {}
    state = {}

    @manager.on("bot_initialized")
    def bot_initialized(bot):
        info = bot.update_player_and_inventory()
        player = info["player"]
        emitted_object = {
            "username": player.username,
            "level": player.level,
            "coordinates": bot.get_position(),
            "storage": {
                "max_item_storage": player.max_item_storage,
                "max_pokemon_storage": player.max_pokemon_storage
            }
        }

        # templates = bot.api_wrapper.download_item_templates().call()
        # print templates

        # reinit state
        state.update(emitted_object)
        state["bot"] = bot

        socketio.emit("bot_initialized", emitted_object, namespace="/event")

    @manager.on("position_updated")
    def position_update(bot, coordinates=None):
        if coordinates is None:
            return
        emitted_object = {
            "coordinates": coordinates
        }
        state["coordinates"] = coordinates
        socketio.emit("position", emitted_object, namespace="/event")

    @manager.on("gyms_found", priority=-2000)
    def gyms_found_event(bot=None, gyms=None):
        if gyms is None or len(gyms) == 0:
            return
        emitted_object = {
            "gyms": JSONEncodable.encode_list(gyms)
        }
        socketio.emit("gyms", emitted_object, namespace="/event")

    @manager.on("pokestops_found", priority=-2000)
    def pokestops_found_event(bot=None, pokestops=None):
        if pokestops is None or len(pokestops) == 0:
            return
        emitted_object = {
            "pokestops": JSONEncodable.encode_list(pokestops)
        }
        socketio.emit("pokestops", emitted_object, namespace="/event")

    @manager.on("pokestop_visited", priority=-2000)
    def pokestop_visited_event(bot=None, pokestop=None):
        if pokestop is None:
            return
        emitted_object = {
            "pokestop": pokestop
        }
        socketio.emit("pokestop_visited", emitted_object, namespace="/event")

    @manager.on("pokemon_caught")
    def pokemon_caught(bot=None, pokemon=None):
        if pokemon is None:
            return
        emitted_object = {
            "pokemon": pokemon.to_json()
        }
        socketio.emit("pokemon_caught", emitted_object, namespace="/event")

    @manager.on("transfer_pokemon")
    def transfer_pokemon(bot=None, pokemon=None):
        if pokemon is None:
            return
        emitted_object = {
            "pokemon": pokemon.to_json()
        }
        socketio.emit("transfer_pokemon", emitted_object, namespace="/event")

    @socketio.on("connect", namespace="/event")
    def connect():
        logger.log("Web client connected", "yellow", fire_event=False)
        if "username" in state:
            emitted_object = state.copy()
            del emitted_object["bot"]
            socketio.emit("bot_initialized", emitted_object, namespace="/event")

    @socketio.on("disconnect", namespace="/event")
    def disconnect():
        logger.log("Web client disconnected", "yellow", fire_event=False)

    @socketio.on("pokemon_list", namespace="/event")
    def client_ask_for_pokemon_list():
        logger.log("Web UI action: Pokemon List", "yellow", fire_event=False)
        bot = state["bot"]
        bot.api_wrapper.get_player().get_inventory()
        inventory = bot.api_wrapper.call()

        emit_object = {
            "pokemon": inventory["pokemon"],
            "candy": inventory["candy"]
        }
        socketio.emit("pokemon_list", emit_object, namespace="/event", room=request.sid)

    @socketio.on("inventory_list", namespace="/event")
    def client_ask_for_inventory_list():
        logger.log("Web UI action: Inventory List", "yellow", fire_event=False)
        bot = state["bot"]
        bot.api_wrapper.get_player().get_inventory()
        inventory = bot.api_wrapper.call()

        emit_object = {
            "inventory": inventory["inventory"]
        }
        socketio.emit("inventory_list", emit_object, namespace="/event", room=request.sid)

    @socketio.on("eggs_list", namespace="/event")
    def client_ask_for_eggs_list():
        logger.log("Web UI action: Eggs List", "yellow", fire_event=False)
        bot = state["bot"]
        bot.api_wrapper.get_player().get_inventory()
        inventory = bot.api_wrapper.call()

        emit_object = {
            "km_walked": inventory["player"].km_walked,
            "eggs": inventory["eggs"],
            "egg_incubators": inventory["egg_incubators"]
        }
        socketio.emit("eggs_list", emit_object, namespace="/event", room=request.sid)

    @socketio.on("evolve_pokemon", namespace="/event")
    def client_ask_for_evolve(evt):
        print evt.id
        logger.log("Web UI action: Evolve", "yellow", fire_event=False)
        bot = state["bot"]

    socketio.run(app, host="0.0.0.0", port=8000, debug=False, use_reloader=False, log_output=False)

WEB_THREAD = Thread(target=run_socket_server)
WEB_THREAD.daemon = True
WEB_THREAD.start()
