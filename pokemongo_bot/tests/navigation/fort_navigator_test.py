import unittest

from api.worldmap import Cell
from pokemongo_bot import FortNavigator
from pokemongo_bot.navigation.destination import Destination
from pokemongo_bot.tests import create_mock_bot


class FortNavigatorTest(unittest.TestCase):

    def test_navigate_pokestops_known(self):
        bot = create_mock_bot({
            "walk": 5,
            "max_steps": 2
        })
        api_wrapper = bot.api_wrapper
        pgoapi = api_wrapper._api

        pgoapi.set_response('fort_details', self._create_pokestop("Test Stop", 51.5043872, -0.0741802))
        pgoapi.set_response('fort_details', self._create_pokestop("Test Stop 2", 51.5060435, -0.073983))

        navigator = FortNavigator(bot)
        map_cells = self._create_map_cells()

        destinations = list()
        for destination in navigator.navigate(map_cells):
            assert isinstance(destination, Destination)

            if len(destinations) == 0:
                assert destination.target_lat == 51.5043872
                assert destination.target_lng == -0.0741802
                assert destination.name == "PokeStop \"Test Stop\""
            elif len(destinations) == 1:
                assert destination.target_lat == 51.5060435
                assert destination.target_lng == -0.073983
                assert destination.name == "PokeStop \"Test Stop 2\""

            destinations.append(destination)

        assert len(destinations) == 2

    def test_navigate_pokestops_unknown(self):
        bot = create_mock_bot({
            "walk": 5,
            "max_steps": 2
        })
        api_wrapper = bot.api_wrapper
        pgoapi = api_wrapper._api

        pgoapi.set_response('fort_details', self._create_pokestop("Test Stop", 51.5043872, -0.0741802))
        pgoapi.set_response('fort_details', {})

        navigator = FortNavigator(bot)
        map_cells = self._create_map_cells()

        destinations = list()
        for destination in navigator.navigate(map_cells):
            assert isinstance(destination, Destination)

            if len(destinations) == 0:
                assert destination.target_lat == 51.5043872
                assert destination.target_lng == -0.0741802
                assert destination.name == "PokeStop \"Test Stop\""
            elif len(destinations) == 1:
                assert destination.target_lat == 51.5060435
                assert destination.target_lng == -0.073983
                assert destination.name == "PokeStop \"Unknown\""

            destinations.append(destination)

        assert len(destinations) == 2

    def _create_map_cells(self):
        return [
            Cell({
                "s2_cell_id": 1,
                "spawn_points": [
                    {
                        "latitude": 0,
                        "longitude": 0
                    }
                ],
                "forts": [
                    self._create_pokestop(1, 51.5043872, -0.0741802),
                    self._create_pokestop(2, 51.5060435, -0.073983),
                ]
            })
        ]

    def _create_pokestop(self, id, lat, lng):
        return {
            "fort_id": str(id),
            "name": str(id),
            "latitude": lat,
            "longitude": lng,
            "enabled": 1,
            "last_modified_timestamp_ms": 0,
            "cooldown_complete_timestamp_ms": 0,
            "type": 1
        }
