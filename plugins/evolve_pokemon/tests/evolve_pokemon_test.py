import unittest

from mock import patch

from api.pokemon import Pokemon
from pokemongo_bot.tests import create_mock_bot
from plugins.evolve_pokemon import after_catch, after_transfer, evolve_pokemon


class EvolvePokemonTest(unittest.TestCase):

    def test_after_catch(self):
        logs = list()

        def log(text, color=None):
            logs.append(text)

        with patch('plugins.evolve_pokemon._log', side_effect=log) as log:

            bot = create_mock_bot({
                'evolve_filter': ['bulbasaur'],
                'evolve_pokemon': True
            })
            api_wrapper = bot.api_wrapper
            pgoapi = api_wrapper._api

            pgoapi.set_response('get_player', {
                'player': {}
            })
            pgoapi.set_response('get_inventory', {
                'inventory_delta': {
                    'inventory_items': [
                        {
                            'inventory_item_data': {
                                'candy': {
                                    'candy': 100,
                                    'family_id': 1
                                }
                            }
                        },
                        {
                            'inventory_item_data': {
                                'pokemon_data': {
                                    "id": 123,
                                    "pokemon_id": 1,
                                    "individual_stamina": 15,
                                    "individual_attack": 15,
                                    "individual_defense": 10,
                                    "cp_multiplier": 0,
                                    "cp": 2000,
                                }
                            }
                        },
                        {
                            'inventory_item_data': {
                                'pokemon_data': {
                                    "id": 1234,
                                    "pokemon_id": 1,
                                    "individual_stamina": 9,
                                    "individual_attack": 9,
                                    "individual_defense": 9,
                                    "cp_multiplier": 0,
                                    "cp": 10,
                                }
                            }
                        }
                    ],
                }
            })

            pgoapi.set_response('evolve_pokemon', {
                'result': 1,
                'evolved_pokemon_data': {
                    "id": 123,
                    "pokemon_id": 2,
                    "individual_stamina": 15,
                    "individual_attack": 15,
                    "individual_defense": 10,
                    "cp_multiplier": 0,
                    "cp": 2000,
                }
            })

            pgoapi.set_response('evolve_pokemon', {
                'result': 1,
                'evolved_pokemon_data': {
                    "id": 1234,
                    "pokemon_id": 2,
                    "individual_stamina": 15,
                    "individual_attack": 15,
                    "individual_defense": 10,
                    "cp_multiplier": 0,
                    "cp": 2000,
                }
            })

            pokemon = self._create_pokemon(123, 1)

            after_catch(bot, pokemon)

            assert len(logs) == 3

            assert logs[0] == 'Evolved Bulbasaur into Ivysaur'
            assert logs[1] == 'Evolved Bulbasaur into Ivysaur'
            assert logs[2] == 'Evolved 2 Pokemon.'

    def test_after_transfer(self):
        logs = list()

        def log(text, color=None):
            logs.append(text)

        with patch('plugins.evolve_pokemon._log', side_effect=log) as log:
            bot = create_mock_bot({
                'evolve_filter': ['bulbasaur'],
                'evolve_pokemon': True
            })
            api_wrapper = bot.api_wrapper
            pgoapi = api_wrapper._api

            pgoapi.set_response('get_player', {
                'player': {}
            })
            pgoapi.set_response('get_inventory', {
                'inventory_delta': {
                    'inventory_items': [
                        {
                            'inventory_item_data': {
                                'candy': {
                                    'candy': 100,
                                    'family_id': 1
                                }
                            }
                        },
                        {
                            'inventory_item_data': {
                                'pokemon_data': {
                                    "id": 123,
                                    "pokemon_id": 1,
                                    "individual_stamina": 15,
                                    "individual_attack": 15,
                                    "individual_defense": 10,
                                    "cp_multiplier": 0,
                                    "cp": 2000,
                                }
                            }
                        },
                        {
                            'inventory_item_data': {
                                'pokemon_data': {
                                    "id": 1234,
                                    "pokemon_id": 1,
                                    "individual_stamina": 9,
                                    "individual_attack": 9,
                                    "individual_defense": 9,
                                    "cp_multiplier": 0,
                                    "cp": 10,
                                }
                            }
                        }
                    ],
                }
            })

            pgoapi.set_response('evolve_pokemon', {
                'result': 1,
                'evolved_pokemon_data': {
                    "id": 123,
                    "pokemon_id": 2,
                    "individual_stamina": 15,
                    "individual_attack": 15,
                    "individual_defense": 10,
                    "cp_multiplier": 0,
                    "cp": 2000,
                }
            })

            pgoapi.set_response('evolve_pokemon', {
                'result': 1,
                'evolved_pokemon_data': {
                    "id": 1234,
                    "pokemon_id": 2,
                    "individual_stamina": 15,
                    "individual_attack": 15,
                    "individual_defense": 10,
                    "cp_multiplier": 0,
                    "cp": 2000,
                }
            })

            pokemon = self._create_pokemon(123, 1)

            after_transfer(bot, pokemon)

            assert len(logs) == 3

            assert logs[0] == 'Evolved Bulbasaur into Ivysaur'
            assert logs[1] == 'Evolved Bulbasaur into Ivysaur'
            assert logs[2] == 'Evolved 2 Pokemon.'

    def test_evolve_pokemon(self):
        logs = list()

        def log(text, color=None):
            logs.append(text)

        with patch('plugins.evolve_pokemon._log', side_effect=log) as log:
            bot = create_mock_bot({
                'evolve_filter': ['bulbasaur'],
                'evolve_pokemon': True
            })
            api_wrapper = bot.api_wrapper
            pgoapi = api_wrapper._api

            pgoapi.set_response('get_player', {
                'player': {}
            })
            pgoapi.set_response('get_inventory', {
                'inventory_delta': {
                    'inventory_items': [
                        {
                            'inventory_item_data': {
                                'candy': {
                                    'candy': 100,
                                    'family_id': 1
                                }
                            }
                        },
                        {
                            'inventory_item_data': {
                                'pokemon_data': {
                                    "id": 123,
                                    "pokemon_id": 1,
                                    "individual_stamina": 15,
                                    "individual_attack": 15,
                                    "individual_defense": 10,
                                    "cp_multiplier": 0,
                                    "cp": 2000,
                                }
                            }
                        },
                        {
                            'inventory_item_data': {
                                'pokemon_data': {
                                    "id": 1234,
                                    "pokemon_id": 1,
                                    "individual_stamina": 9,
                                    "individual_attack": 9,
                                    "individual_defense": 9,
                                    "cp_multiplier": 0,
                                    "cp": 10,
                                }
                            }
                        }
                    ],
                }
            })

            pgoapi.set_response('evolve_pokemon', {
                'result': 1,
                'evolved_pokemon_data': {
                    "id": 123,
                    "pokemon_id": 2,
                    "individual_stamina": 15,
                    "individual_attack": 15,
                    "individual_defense": 10,
                    "cp_multiplier": 0,
                    "cp": 2000,
                }
            })

            pgoapi.set_response('evolve_pokemon', {
                'result': 1,
                'evolved_pokemon_data': {
                    "id": 1234,
                    "pokemon_id": 2,
                    "individual_stamina": 15,
                    "individual_attack": 15,
                    "individual_defense": 10,
                    "cp_multiplier": 0,
                    "cp": 2000,
                }
            })

            pokemon = self._create_pokemon(123, 1)

            evolve_pokemon(bot, evolve_list=[pokemon])

            assert len(logs) == 2

            assert logs[0] == 'Evolved Bulbasaur into Ivysaur'
            assert logs[1] == 'Evolved 1 Pokemon.'

    @staticmethod
    def _create_pokemon(uid, pid):
        return Pokemon({
            "id": int(uid),
            "pokemon_id": int(pid),
            "individual_stamina": 15,
            "individual_attack": 15,
            "individual_defense": 10,
            "cp_multiplier": 0,
            "cp": 2000,
        })
