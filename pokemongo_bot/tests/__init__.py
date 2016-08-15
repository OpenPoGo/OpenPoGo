import logging
import os
from argparse import Namespace

from mock import Mock, MagicMock

import pokemongo_bot
from pokemongo_bot import FortNavigator
from pokemongo_bot import PluginManager
from pokemongo_bot.event_manager import EventManager
from pokemongo_bot.mapper import Mapper
from pokemongo_bot.navigation.path_finder import DirectPathFinder
from pokemongo_bot.stepper import Stepper
import pgoapi
import api


# pylint: disable=super-init-not-called
class PGoApiMock(pgoapi.PGoApi):
    def __init__(self):
        self.positions = list()
        self.call_responses = list()
        self.should_login = True

    # pylint: disable=unused-argument
    def activate_signature(self, shared_lib):
        return None

    # pylint: disable=unused-argument
    def login(self, provider, username, password, lat=None, lng=None, alt=None, app_simulation=True):
        print("login: {}".format(self.should_login))
        return self.should_login

    def set_position(self, lat, lng, alt):
        self.positions.append((lat, lng, alt))
        return None

    def get_position(self):
        return self.positions[len(self.positions) - 1]

    # pylint: disable=no-self-use
    def list_curr_methods(self):
        return list()

    def set_response(self, call_type, response):
        self.call_responses.append((call_type, response))

    def create_request(self):
        return PGoApiRequestMock(self)

    def call_stack_size(self):
        return len(self.call_responses)


# pylint: disable=super-init-not-called
class PGoApiRequestMock(pgoapi.pgoapi.PGoApiRequest):
    def __init__(self, pgo):
        self.pgoapi = pgo
        self.calls = []

    def call(self):
        return_values = {}

        for call in self.calls:
            call_name, _, _ = call
            if len(self.pgoapi.call_responses) == 0:
                raise RuntimeError("Response for \"{}\" expected, but none was set".format(call_name))

            call_response_name, call_response_data = self.pgoapi.call_responses.pop(0)

            if call_name.upper() != call_response_name.upper():
                raise RuntimeError(
                    "Response expected for \"{}\", but the next response was for \"{}\"".format(call_name,
                                                                                                call_response_name))

            if call_response_data is not None:
                return_values[call_response_name.upper()] = call_response_data

        if len(return_values) > 0:
            return {
                'status_code': 1,
                'responses': return_values
            }
        else:
            return None

    def __getattr__(self, func):

        def function(*args, **kwargs):
            func_name = str(func).upper()
            self.calls.append((func_name, args, kwargs))
            return self

        return function


def create_mock_api_wrapper():
    pgoapi_instance = PGoApiMock()
    api_wrapper = api.PoGoApi(api=pgoapi_instance)
    api_wrapper.get_expiration_time = MagicMock(return_value=1000000)
    api_wrapper.set_position(0, 0, 0)
    return api_wrapper


def create_test_config(user_config=None):
    if user_config is None:
        user_config = {}

    config = {
        "debug": False,
        "path_finder": None,
        "walk": 4.16,
        "max_steps": 2,
    }
    config.update(user_config)

    return Namespace(**config)


def create_mock_bot(user_config=None):
    config_namespace = create_test_config(user_config)

    api_wrapper = create_mock_api_wrapper()
    plugin_manager = PluginManager(os.path.dirname(os.path.realpath(__file__)) + '/plugins')
    mapper = Mapper(config_namespace, api_wrapper)
    path_finder = DirectPathFinder(config_namespace)
    stepper = Stepper(config_namespace, api_wrapper, path_finder)
    navigator = FortNavigator(config_namespace, api_wrapper)
    log = logging.getLogger(__name__)
    event_manager = EventManager()

    bot = pokemongo_bot.PokemonGoBot(config_namespace, api_wrapper, plugin_manager, event_manager, mapper, stepper,
                                     navigator, log)

    return bot
