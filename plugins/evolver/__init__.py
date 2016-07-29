import json

from pokemongo_bot import logger
from pokemongo_bot import manager
from pokemongo_bot import sleep


@manager.on('after_catch_pokemon')
def _after_catch(name=None, bot=None):
    _do_evolve(bot, name)


@manager.on('after_transfer_pokemon')
def _after_transfer(name=None, bot=None):
    _do_evolve(bot, name)


def _do_evolve(bot, name):
    if bot.config.evolve_pokemon:
        pokemon_group = bot.get_pokemon()
        pokemon_name = _get_base_pokemon(bot, name)
        pokemon_candies = bot.candies[pokemon_name]
        for pokemon in bot.pokemon_list:
            if pokemon["Name"] is pokemon_name:
                pokemon_id = pokemon['Number']
                num_evolve = pokemon.get('Next Evolution Requirements.Amount', None)
                if num_evolve is None:
                    logger.log('[#] Can\'t evolve {}'.format(pokemon_name), 'yellow')
                    break

                pokemon_evolve = pokemon_group.get(int(pokemon_id), None)
                if pokemon_evolve is None:
                    break

                group_cp = pokemon_evolve.keys()
                group_cp.sort()
                group_cp.reverse()

                num_evolved = 0
                while num_evolve < pokemon_candies and group_cp:
                    bot.api.evolve_pokemon(pokemon_id=pokemon_evolve[group_cp[0]])
                    response = bot.api.call()
                    status = response['responses']['EVOLVE_POKEMON']['result']
                    if status == 1:
                        del group_cp[0]
                        pokemon_candies -= (num_evolve - 1)
                        num_evolved += 1
                        sleep(2)
                    else:
                        logger.log(response['responses']['EVOLVE_POKEMON'].encode('utf-8', 'ignore'), 'red')
                        break

                if num_evolve > pokemon_candies:
                    logger.log('[#] Not enough candies for {} to evolve'.format(pokemon_name), 'yellow')
                elif group_cp:
                    logger.log('[#] Stopped evolving due to error', 'red')
                else:
                    logger.log('[#] Evolved {} {}'.format(num_evolved, pokemon_name), 'green')
        #update candies
        bot.update_inventory()
        bot.get_pokemon()

def _get_base_pokemon(bot, name):
    pokemon_name = name
    for pokemon in bot.pokemon_list:
        if pokemon['Name'] is not pokemon_name:
            continue
        else:
            previous_evolutions = pokemon.get("Previous evolution(s)", [])
            if previous_evolutions:
                pokemon_name = previous_evolutions[0]['Name']
            else:
                pokemon_name = name
            break
    return pokemon_name
