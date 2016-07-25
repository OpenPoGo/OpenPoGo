# -*- coding: utf-8 -*-

from events import IEventHandler

class BotStartHandler(IEventHandler):
    handles = 'before_cell_work'

    def process(self, **kwargs):
        if self.bot.process_ignored_pokemon:
            try:
                for cell in map_cells:
                    for p in cell['wild_pokemons'][:]:
                        pokemon_id = p['pokemon_data']['pokemon_id']
                        pokemon_name = filter(lambda x: int(x.get('Number')) == pokemon_id, self.bot.pokemon_list)[0]['Name']

                        if pokemon_name in ignores:
                            kwargs['cell']['wild_pokemons'].remove(p)
            except KeyError:
                pass

            try:
                for call in map_cells:
                    for p in cell['catchable_pokemons'][:]:
                        pokemon_id = p['pokemon_id']
                        pokemon_name = filter(lambda x: int(x.get('Number')) == pokemon_id, self.bot.pokemon_list)[0]['Name']

                        if pokemon_name in ignores:
                            kwargs['cell']['catchable_pokemons'].remove(p)
            except KeyError:
                pass