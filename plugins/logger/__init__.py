from pokemongo_bot import logger, event_manager
from pokemongo_bot.event_manager import manager

# pylint: disable=unused-argument

@manager.on("before_catch_pokemon")
def action_before_catch_pokemon(event, name=None, combat_power=None, pokemon_potential=None, **kwargs):
    logger.log("[#] A Wild {} appeared! [CP {}] [Potential {}]".format(name, combat_power, pokemon_potential), "yellow")

@manager.on("catch_pokemon")
def action_catch_pokemon(hook_params):
    pass

@manager.on("pokemon_catch_fail")
def action_pokemon_catch_fail(event, pokeball_name=None, **kwargs):
    logger.log("[-] Attempted to capture {} - failed.. trying again!".format(pokeball_name))

@manager.on("pokemon_catch_flee")
def action_pokemon_catch_flee(event, pokeball_name=None, **kwargs):
    logger.log("[-] Oh no! {} vanished! :(".format(pokeball_name))

@manager.on("after_catch_pokemon")
def action_after_catch_pokemon(event, name=None, combat_power=None, **kwargs):
    logger.log("[x] Captured {} [CP {}]".format(name, combat_power), "green")

@manager.on("use_pokeball")
def action_use_pokeball(event, pokeball_name=None, number_left=None, **kwargs):
    logger.log("[x] Using {}... ({} left!)".format(pokeball_name, number_left))

@manager.on("transfer_pokemon")
def action_transfer_pokemon(event, group_id=None, pokemon=None, **kwargs):
    logger.log("[x] Transfering {}!)".format(pokemon))

@manager.on("transfer_done")
def action_transfer_done(event, **kwargs):
    logger.log("[x] Transferring Done")

@manager.on("recycle_item")
def action_recycle_item(event, item=None, amount=None, **kwargs):
    logger.log("[+] Recycling: {} x {}...".format(amount, item))

@manager.on("fort_arrived")
def action_fort_arrived(event, name, **kwargs):
    logger.log("[+] Now at Pokestop {}".format(name))

@manager.on("fort_spinned")
def action_fort_spinned(event, rewards=None, **kwargs):
    logger.log("[+] Fort spinned rewards: {}".format(', '.join(rewards)))

