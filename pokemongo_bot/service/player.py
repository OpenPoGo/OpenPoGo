from app import kernel
from pokemongo_bot.item_list import Item
from pokemongo_bot.human_behaviour import sleep


@kernel.container.register('player_service', ['@api_wrapper', '@event_manager', '@logger'])
class Player(object):
    def __init__(self, api_wrapper, event_manager, logger):
        self._api_wrapper = api_wrapper
        self._event_manager = event_manager
        self._logger = logger.getLogger()
        self._logger_egg = logger.getLogger('Egg')
        self._logged_in = False

        self._eggs = None
        self._egg_incubators = []
        self._candies = {}
        self._pokeballs = {
            Item.ITEM_POKE_BALL.value: 0,
            Item.ITEM_GREAT_BALL.value: 0,
            Item.ITEM_ULTRA_BALL.value: 0,
            Item.ITEM_MASTER_BALL.value: 0
        }
        self._player = None
        self._inventory = None
        self._pokemon = None

    def login(self):
        self._logged_in = self._api_wrapper.login()
        return self._logged_in

    def update(self, do_sleep=True):
        response_dict = self._api_wrapper.get_player().get_inventory().call()

        if do_sleep:
            sleep(2)

        if response_dict is None:
            self._logger.error('Failed to retrieve player and inventory stats', 'red')
            return False

        self._player = response_dict['player']
        self._inventory = response_dict['inventory']
        self._candies = response_dict['candy']
        self._pokemon = response_dict['pokemon']
        self._candies = response_dict['candy']
        self._eggs = response_dict['eggs']
        self._egg_incubators = response_dict['egg_incubators']

        for item_id in self._inventory:
            if item_id in self._pokeballs:
                self._pokeballs[item_id] = self._inventory[item_id]

        self._event_manager.fire('service_player_updated', data=self)

        return True

    def get_player(self):
        self.update()
        return self._player

    def get_inventory(self):
        self.update()
        return self._inventory

    def get_eggs(self):
        self.update()
        return self._eggs

    def get_egg_incubators(self):
        self.update()
        return self._egg_incubators

    def get_pokemon(self):
        self.update()
        return self._pokemon

    def get_candies(self):
        self.update()
        return self._candies

    def get_candy(self, pokemon_id):
        self.update()
        try:
            return self._candies[pokemon_id]
        except KeyError:
            return 0

    def add_candy(self, pokemon_id, pokemon_candies):
        pokemon_id = int(pokemon_id)
        if pokemon_id in self._candies:
            self._candies[pokemon_id] += int(pokemon_candies)
        else:
            self._candies[pokemon_id] = int(pokemon_candies)

    def get_pokeballs(self):
        self.update()
        return self._pokeballs

    def print_stats(self):
        if self.update() is True:
            self._logger.info('')
            self._logger.info('Username: {}'.format(self._player.username))
            self._logger.info('Account creation: {}'.format(self._player.get_creation_date()))
            self._logger.info('Bag storage: {}/{}'.format(self._inventory['count'], self._player.max_item_storage))
            self._logger.info('Pokemon storage: {}/{}'.format(len(self._pokemon) + len(self._eggs), self._player.max_pokemon_storage))
            self._logger.info('Stardust: {:,}'.format(self._player.stardust))
            self._logger.info('Pokecoins: {}'.format(self._player.pokecoin))
            self._logger.info('Poke Balls: {}'.format(self._pokeballs[1]))
            self._logger.info('Great Balls: {}'.format(self._pokeballs[2]))
            self._logger.info('Ultra Balls: {}'.format(self._pokeballs[3]))
            self._logger.info('-- Level: {}'.format(self._player.level))
            self._logger.info('-- Experience: {:,}'.format(self._player.experience))
            self._logger.info('-- Experience until next level: {:,}'.format(self._player.next_level_xp - self._player.experience))
            self._logger.info('-- Pokemon captured: {:,}'.format(self._player.pokemons_captured))
            self._logger.info('-- Pokestops visited: {:,}'.format(self._player.poke_stop_visits))

    def heartbeat(self):
        self._api_wrapper.get_hatched_eggs()
        self._api_wrapper.check_awarded_badges()

        self.update(do_sleep=False)

        if len(self._player.hatched_eggs):
            self._player.hatched_eggs.pop(0)
            self._logger_egg.info("Hatched an egg!", "green")

    def get_hatched_eggs(self):
        self._api_wrapper.get_hatched_eggs().call()
        if len(self._player.hatched_eggs):
            self._player.hatched_eggs.pop(0)
            self._logger_egg.info("Hatched an egg!", "green")

    def check_awarded_badges(self):
        self._api_wrapper.check_awarded_badges().call()
