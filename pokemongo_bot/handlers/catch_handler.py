# -*- coding: utf-8 -*-

from cell_workers import PokemonCatchWorker
from cell_workers.utils import distance
from events import IEventHandler

class CatchablePokemonHandler(IEventHandler):
    handles = 'cell_work_cachable_pokemon'

    def process(self, **kwargs):
        for cell in kwargs['map_cells']:
            if 'catchable_pokemons' in cell and len(cell['catchable_pokemons']) > 0:
                #logger.log('[#] Something rustles nearby!')
                # Sort all by distance from current pos- eventually this should
                # build graph & A* it
                cell['catchable_pokemons'].sort(
                    key=lambda x: distance(self.bot.position[0], self.bot.position[1], x['latitude'], x['longitude']))
                for pokemon in cell['catchable_pokemons']:
                    with open('web/catchable-%s.json' % (self.bot.config.username), 'w') as outfile:
                        json.dump(pokemon, outfile)
                    worker = PokemonCatchWorker(pokemon, self.bot)
                    if worker.work() == -1:
                        break
                    with open('web/catchable-%s.json' % (self.bot.config.username), 'w') as outfile:
                        json.dump({}, outfile)


class WildPokemonHandler(IEventHandler):
    handles = 'cell_work_wild_pokemon'

    def process(self, **kwargs):
        for cell in kwargs['map_cells']:
            if 'wild_pokemons' in cell and len(cell['wild_pokemons']) > 0:
                # Sort all by distance from current pos- eventually this should
                # build graph & A* it
                cell['wild_pokemons'].sort(
                    key=lambda x: distance(self.bot.position[0], self.bot.position[1], x['latitude'], x['longitude']))
                for pokemon in cell['wild_pokemons']:
                    worker = PokemonCatchWorker(pokemon, self.bot)
                    if worker.work() == -1:
                        break