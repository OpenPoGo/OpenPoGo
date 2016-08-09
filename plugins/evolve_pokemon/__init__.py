from pokemongo_bot import logger
from pokemongo_bot import manager
from pokemongo_bot import sleep

# pylint: disable=unused-argument


@manager.on('caught_pokemon', priority=0)
def after_catch(bot, pokemon=None):
    # type: (PokemonGoBot, Pokemon) -> None
    _do_evolve_by_group(bot, bot.pokemon_list[pokemon.pokemon_id - 1]['Name'])


@manager.on('after_transfer_pokemon', priority=0)
def after_transfer(bot, pokemon=None):
    # type: (PokemonGoBot, Pokemon) -> None
    _do_evolve_by_group(bot, bot.pokemon_list[pokemon.pokemon_id - 1]['Name'])


@manager.on("evolve_pokemon", priority=0)
def evolve_pokemon(bot, evolve_list=None):
    # type: (PokemonGoBot, List[Pokemon]) -> None
    _do_evolve(bot, evolve_list=evolve_list)


def _do_evolve_by_group(bot, name):
    # type: (PokemonGoBot, str) -> None
    response_dict = bot.update_player_and_inventory()
    pokemon_list = response_dict['pokemon']
    base_pokemon = _get_base_pokemon(bot, name)
    base_name = base_pokemon['name']
    pokemon_id = base_pokemon['id']
    num_evolve = base_pokemon['requirements']
    evolve_list = [str.lower(str(x)) for x in bot.config.evolve_filter]

    if base_name.lower() in evolve_list or 'all' in evolve_list:
        if num_evolve is None:
            _log('Can\'t evolve {}'.format(base_name), color='yellow')
            return

        pokemon_evolve = [pokemon for pokemon in pokemon_list if pokemon.pokemon_id is pokemon_id]
        if pokemon_evolve is None:
            return
        pokemon_evolve.sort(key=lambda p: p.combat_power, reverse=True)
        _do_evolve(bot, pokemon_evolve)


def _do_evolve(bot, evolve_list=None):
    # type: (PokemonGoBot, List[Pokemon]) -> None

    if not bot.config.evolve_pokemon:
        return

    bot.update_player_and_inventory()

    if evolve_list is None or len(evolve_list) == 0:
        _log("No Pokemon to evolve.", color="yellow")

    num_evolved = 0
    pokemon_candies = dict()

    for pokemon in evolve_list:
        pokemon_id = int(pokemon.pokemon_id)
        pokemon_name = bot.pokemon_list[pokemon_id - 1]["Name"]

        base_pokemon = _get_base_pokemon(bot, pokemon_name)
        base_name = base_pokemon['name']
        base_id = base_pokemon['id']
        num_for_evolve = base_pokemon['requirements']

        if pokemon_id not in pokemon_candies:
            pokemon_candies[base_id] = bot.candies.get(base_id, 0)

        if pokemon_candies[base_id] < num_for_evolve:
            _log('Not enough candies for {} to evolve'.format(base_name), color='yellow')
        else:
            response = bot.api_wrapper.evolve_pokemon(pokemon_id=pokemon.unique_id).call()

            if response['evolution'].success:
                pokemon_candies[base_id] -= (num_for_evolve - 1)
                num_evolved += 1
                evolved_id = response['evolution'].get_pokemon().pokemon_id
                _log('Evolved {} into {}'.format(base_name, bot.pokemon_list[evolved_id - 1]['Name']))
                sleep(2)
            else:
                _log('Evolving {} failed'.format(base_name), color='red')
                break
            sleep(2)

    _log("Evolved {} Pokemon.".format(num_evolved))


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


def _log(text, color='green'):
    logger.log(text, color=color, prefix='Evolve')
