from api.pokemon import Pokemon
from pokemongo_bot.human_behaviour import sleep
from pokemongo_bot.event_manager import manager
from pokemongo_bot import logger
from plugins.transfer_pokemon.config import release_rules


def get_transfer_list(bot, transfer_list=None):
    if transfer_list is None:
        bot.api_wrapper.get_player().get_inventory()
        response_dict = bot.api_wrapper.call()
        transfer_list = response_dict['pokemon']

    return None if len(transfer_list) == 0 else transfer_list


def get_indexed_pokemon(bot, transfer_list=None):
    transfer_list = get_transfer_list(bot, transfer_list)
    if transfer_list is None:
        return None

    indexed_pokemon = dict()
    for deck_pokemon in transfer_list:
        pokemon_num = deck_pokemon.pokemon_id
        if pokemon_num not in indexed_pokemon:
            indexed_pokemon[pokemon_num] = list()
        indexed_pokemon[pokemon_num].append(deck_pokemon)

    return indexed_pokemon


# Filters Pokemon deployed at gyms
# Never disable as it might lead to a ban!
@manager.on("pokemon_bag_full", priority=-50)
def filter_deployed_pokemon(bot, transfer_list=None, filter_list=None):
    # type: (PokemonGoBot, Optional[List[Pokemon]]), Optional[List[str]] -> Dict[Str, List]

    filter_list = [] if filter_list is None else filter_list
    transfer_list = get_transfer_list(bot, transfer_list)
    if transfer_list is None:
        return False

    new_transfer_list = [deck_pokemon for deck_pokemon in transfer_list if deck_pokemon.deployed_fort_id is None]

    if len(new_transfer_list) != len(transfer_list):
        filter_list.append("excluding Pokemon at gyms")

    return {"transfer_list": new_transfer_list, "filter_list": filter_list}


# Filters favorited Pokemon
# Never disable as it might lead to a ban!
@manager.on("pokemon_bag_full", priority=-40)
def filter_favorited_pokemon(bot, transfer_list=None, filter_list=None):
    # type: (PokemonGoBot, Optional[List[Pokemon]]), Optional[List[str]] -> Dict[Str, List]

    filter_list = [] if filter_list is None else filter_list
    transfer_list = get_transfer_list(bot, transfer_list)
    if transfer_list is None:
        return False

    new_transfer_list = [deck_pokemon for deck_pokemon in transfer_list if deck_pokemon.favorite is False]

    if len(new_transfer_list) != len(transfer_list):
        filter_list.append("excluding favorited Pokemon")

    return {"transfer_list": new_transfer_list, "filter_list": filter_list}


# Wraps a caught Pokemon into a list for transferring
@manager.on("pokemon_caught", priority=-30)
def wrap_pokemon_in_list(transfer_list=None, pokemon=None):
    if pokemon is None:
        return

    if transfer_list is None:
        transfer_list = []

    transfer_list.append(pokemon)
    return {"transfer_list": transfer_list}


# Filters Pokemon based on ignore/always keep list
@manager.on("pokemon_bag_full", "pokemon_caught", priority=-20)
def filter_pokemon_by_ignore_list(bot, transfer_list=None, filter_list=None):
    # type: (PokemonGoBot, Optional[List[Pokemon]]), Optional[List[str]] -> Dict[Str, List]

    filter_list = [] if filter_list is None else filter_list
    transfer_list = get_transfer_list(bot, transfer_list)
    if transfer_list is None:
        return False

    ignore_list = bot.config.ign_init_trans.split(',')

    new_transfer_list = []
    excluded_species = set()
    for pokemon in transfer_list:
        species_num = pokemon.pokemon_id
        species_name = bot.pokemon_list[species_num - 1]["Name"]
        if str(species_num) not in ignore_list and species_name not in ignore_list:
            new_transfer_list.append(pokemon)
        else:
            excluded_species.add(species_name)

    if len(new_transfer_list) != len(transfer_list):
        if len(excluded_species) > 1:
            excluded_species_list = list(excluded_species)
            filter_list.append("excluding " + "s, ".join(excluded_species_list[:-1]) + "s and " + excluded_species_list[-1] + "s")
        else:
            filter_list.append("excluding " + excluded_species.pop() + "s")

    return {"transfer_list": new_transfer_list, "filter_list": filter_list}


# TODO: Fix this function to use dependency injection for release rules
@manager.on("pokemon_bag_full", "pokemon_caught", priority=-10)
def filter_pokemon_by_cp_iv(bot, transfer_list=None, filter_list=None):
    # type: (PokemonGoBot, Optional[List[Pokemon]]), Optional[List[str]] -> Dict[Str, List]

    filter_list = [] if filter_list is None else filter_list
    transfer_list = get_transfer_list(bot, transfer_list)
    if transfer_list is None:
        return False

    default_rules = {
        'release_below_cp': bot.config.cp,
        'release_below_iv': bot.config.pokemon_potential,
        'logic': 'and',
    }

    indexed_pokemon = get_indexed_pokemon(bot, transfer_list)

    if release_rules:
        filter_list.append("according to per-species CP/IV rules")
    else:
        filter_list.append("with CP <= {} and IV <= {}".format(bot.config.cp, bot.config.pokemon_potential))

    pokemon_groups = list(indexed_pokemon.keys())
    for pokemon_group in pokemon_groups:

        # skip if it's our only pokemon of this type
        if len(indexed_pokemon[pokemon_group]) < 2:
            del indexed_pokemon[pokemon_group]
            continue

        # Load rules for this group. If rule doesnt exist make one with default settings.
        pokemon_name = bot.pokemon_list[pokemon_group - 1]["Name"]
        pokemon_rules = release_rules.get(pokemon_name, default_rules)
        cp_threshold = pokemon_rules.get('release_below_cp', bot.config.cp)
        iv_threshold = pokemon_rules.get('release_below_iv', bot.config.pokemon_potential)
        rules_logic = pokemon_rules.get('logic', 'and')

        # only keep everything below specified CP
        group_transfer_list = []
        for deck_pokemon in indexed_pokemon[pokemon_group]:

            # is the Pokemon's CP less than our set threshold?
            within_cp = (deck_pokemon.combat_power <= cp_threshold)

            # is the Pokemon's IV less than our set threshold?
            within_potential = (deck_pokemon.potential <= iv_threshold)

            # if we are using AND logic and both are true, transfer
            if rules_logic == 'and' and (within_cp and within_potential):
                group_transfer_list.append(deck_pokemon)

            # if we are using OR logic and either is true, transfer
            elif rules_logic == 'or' and (within_cp or within_potential):
                group_transfer_list.append(deck_pokemon)

        # Check if we are trying to remove all the pokemon in this group.
        if len(group_transfer_list) == len(indexed_pokemon[pokemon_group]):
            # Sort by CP * potential and keep the best one
            indexed_pokemon[pokemon_group].sort(key=lambda p: p.combat_power * p.potential)
            indexed_pokemon[pokemon_group] = indexed_pokemon[pokemon_group][:-1]
        else:
            indexed_pokemon[pokemon_group] = group_transfer_list

    new_transfer_list = []
    pokemon_groups = list(indexed_pokemon.keys())
    for pokemon_group in pokemon_groups:
        for deck_pokemon in indexed_pokemon[pokemon_group]:
            new_transfer_list.append(deck_pokemon)

    return {"transfer_list": new_transfer_list, "filter_list": filter_list}


@manager.on("pokemon_bag_full", "transfer_pokemon", "pokemon_caught", priority=0)
def transfer_pokemon(bot, transfer_list=None, filter_list=None):
    # type: (PokemonGoBot, Optional[List[Pokemon]], Optional[List[str]]) -> None

    filter_list = [] if filter_list is None else filter_list

    def log(text, color="black"):
        logger.log(text, color=color, prefix="Transfer")

    if transfer_list is None or len(transfer_list) == 0:
        return False

    output_str = "Transferring {} Pokemon".format(len(transfer_list))

    # Print out the list of filters used
    filter_list = filter_list[::-1]
    if len(filter_list) > 1:
        output_str += " " + ", ".join(filter_list[:-1]) + " and " + filter_list[-1]
    elif len(filter_list) == 1:
        output_str += " " + filter_list[0]

    log(output_str)

    for index, pokemon in enumerate(transfer_list):
        pokemon_num = pokemon.pokemon_id
        pokemon_name = bot.pokemon_list[pokemon_num - 1]["Name"]
        pokemon_cp = pokemon.combat_power
        pokemon_potential = pokemon.potential
        log("Transferring {0} (#{1}) with CP {2} and IV {3} ({4}/{5})".format(pokemon_name,
                                                                              pokemon_num,
                                                                              pokemon_cp,
                                                                              pokemon_potential,
                                                                              index+1,
                                                                              len(transfer_list)))

        bot.api_wrapper.release_pokemon(pokemon_id=pokemon.unique_id).call()
        sleep(2)
        bot.add_candies(name=pokemon_name, pokemon_candies=1)
        bot.fire('after_transfer_pokemon', pokemon=pokemon)

    log("Transferred {} Pokemon.".format(len(transfer_list)))
