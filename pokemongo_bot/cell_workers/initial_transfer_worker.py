from pokemongo_bot.human_behaviour import sleep
from pokemongo_bot import logger


class InitialTransferWorker(object):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.pokemon_list = bot.pokemon_list
        self.api = bot.api

    def work(self):
        logger.log('[x] Initial Transfer.')
        ignlist = self.config.ign_init_trans.split(',')

        if self.config.cp:
            logger.log('[x] Will NOT transfer anything above CP {} or these {}'.format(
                self.config.cp, ignlist))
        else:
            logger.log('[x] Preparing to transfer all Pokemon duplicates, keeping the highest CP of each one type.')

        pokemon_groups = self.bot.get_pokemon()

        for group_id in pokemon_groups:

            group_cp = pokemon_groups[group_id].keys()

            if len(group_cp) > 1:
                group_cp.sort()
                group_cp.reverse()

                pokemon = self.pokemon_list[int(group_id - 1)]
                pokemon_name = pokemon['Name']
                pokemon_num = pokemon['Number'].lstrip('0')

                for i in range(1, len(group_cp)):

                    if (self.config.cp and group_cp[i] > self.config.cp) or (pokemon_name in ignlist or pokemon_num in ignlist):
                        continue

                    logger.log('[x] Transferring #{} ({}) with CP {}'.format(group_id, pokemon_name, group_cp[i]))
                    self.api.release_pokemon(pokemon_id=pokemon_groups[group_id][group_cp[i]])
                    # Not using the response from API at the moment; commenting out to pass pylint
                    # response_dict = self.api.call()
                    self.api.call()

                    self.bot.add_candies(name=pokemon_name, pokemon_candies=1)
                    sleep(2)
                    self.bot.fire('after_transfer_pokemon', name=pokemon_name)

        logger.log('[x] Transferring Done.')
