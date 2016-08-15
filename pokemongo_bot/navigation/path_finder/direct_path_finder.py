from pokemongo_bot.navigation.path_finder.path_finder import PathFinder
from app import service_container


# pylint: disable=unused-argument,no-self-use

@service_container.register('direct_path_finder', ['@config'])
class DirectPathFinder(PathFinder):
    def path(self, from_lat, form_lng, to_lat, to_lng):
        # type: (float, float, float, float) -> List[(float, float)]
        return [
            (to_lat, to_lng)
        ]
