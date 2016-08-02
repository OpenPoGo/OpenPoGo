from pokemongo_bot import logger
from pokemongo_bot import manager
from pokemongo_bot import sleep

# pylint: disable=unused-argument

@manager.on('caught_pokemon')
def _after_catch(event, name=None, bot=None, combat_power=None, pokemon_potential=None):
    _do_evolve(bot, name)

@manager.on('after_transfer_pokemon')
def _after_transfer(event, name=None, bot=None):
    _do_evolve(bot, name)

def _do_evolve(bot, name):
    if bot.config.evolve_pokemon:
        bot.api_wrapper.get_player().get_inventory()
        response_dict = bot.api_wrapper.call()
        pokemon_list = response_dict['pokemon']
        base_pokemon = _get_base_pokemon(bot, name)
        base_name = base_pokemon['name']
        pokemon_id = base_pokemon['id']
        num_evolve = base_pokemon['requirements']
        pokemon_candies = bot.candies.get(int(pokemon_id), 0)
        if pokemon_id in bot.config.evolve_filter:
            if num_evolve is None:
                logger.log('[#] Can\'t evolve {}'.format(base_name), 'yellow')
                return

            pokemon_evolve = [pokemon for pokemon in pokemon_list if pokemon.pokemon_id is pokemon_id]
            if pokemon_evolve is None:
                return
            pokemon_evolve.sort(key=lambda p: p.combat_power, reverse=True)

            num_evolved = 0
            while num_evolve < pokemon_candies and pokemon_evolve:
                bot.api_wrapper.evolve_pokemon(pokemon_id=pokemon_evolve[0].unique_id)
                response = bot.api_wrapper.call()
                if response['evolution'].success:
                    del pokemon_evolve[0]
                    pokemon_candies -= (num_evolve - 1)
                    num_evolved += 1
                    sleep(2)
                else:
                    logger.log('Evolving {} failed'.format(base_name), 'red')
                    break

            if num_evolve > pokemon_candies and num_evolved is 0:
                logger.log('[#] Not enough candies for {} to evolve'.format(base_name), 'yellow')
            elif pokemon_evolve:
                logger.log('[#] Stopped evolving due to error', 'red')
            else:
                logger.log('[#] Evolved {} {}(s)'.format(num_evolved, base_name), 'green')

        # bot.update_inventory()
        # bot.get_pokemon()

def _get_base_pokemon(bot, name):
    pokemon_id = None
    num_evolve = None
    pokemon_name = name
    for pokemon in bot.pokemon_list:
        if pokemon['Name'] is not name:
            continue
        else:
            previous_evolutions = pokemon.get("Previous evolution(s)", [])
            if previous_evolutions:
                pokemon_id = previous_evolutions[0]['Number']
                pokemon_name = previous_evolutions[0]['Name']
                num_evolve = bot.pokemon_list[int(pokemon_id) - 1].get('Next Evolution Requirements', None)
                if num_evolve is not None:
                    num_evolve = num_evolve.get('Amount', None)
            else:
                pokemon_id = pokemon['Number']
                num_evolve = pokemon.get('Next Evolution Requirements', None)
                if num_evolve is not None:
                    num_evolve = num_evolve.get('Amount', None)
            break
    return {'id': int(pokemon_id), 'requirements': num_evolve, 'name': pokemon_name}
