from pokemongo_bot.event_manager import manager

# pylint: disable=unused-variable, unused-argument

bot_contexts = dict()
enabled_events = list()


@manager.on('bot_initialized')
def bot_initialized_event(bot):
    bot_contexts[bot.config.username] = bot

    if isinstance(bot.config.web_events, bool):
        if bot.config.web_events:
            enabled_events.append('transfer_pokemon')
            enabled_events.append('evolve_pokemon')


def log(text, color='black'):
    manager.fire('logging', text=text, color=color, prefix='Transfer')


@manager.on('web_transfer_pokemon')
def transfer(payload):
    if 'transfer_pokemon' in enabled_events:
        if 'user_id' not in payload or 'pokemon_id' not in payload and payload['user_id'] not in bot_contexts:
            return

        bot = bot_contexts[payload['user_id']]
        inventory = bot.update_player_and_inventory()

        for pokemon in inventory['pokemon']:
            if pokemon.unique_id == payload['pokemon_id']:
                bot.fire('transfer_pokemon', transfer_list=[pokemon])
                return

    log('[#] No pokemon found with ID {}'.format(str(payload['pokemon_id'])), 'red')


@manager.on('web_evolve_pokemon')
def evolve(payload):
    if 'evolve_pokemon' in enabled_events:
        if 'user_id' not in payload or 'pokemon_id' not in payload and payload['user_id'] not in bot_contexts:
            return

        bot = bot_contexts[payload['user_id']]
        inventory = bot.update_player_and_inventory()

        for pokemon in inventory['pokemon']:
            if pokemon.unique_id == payload['pokemon_id']:
                bot.fire('evolve_pokemon', evolve_list=[pokemon])
                return

    log('[#] No pokemon found with ID {}'.format(str(payload['pokemon_id'])), 'red')
