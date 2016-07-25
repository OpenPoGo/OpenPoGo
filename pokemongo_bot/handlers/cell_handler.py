# -*- coding: utf-8 -*-

from events import IEventHandler

class CellHandler(IEventHandler):
    handles = 'cell_work'

    def process(self, **kwargs):
        if (self.bot.config.mode == "all" or self.bot.config.mode == "poke"):
            self.event_manager.emit_event('cell_work_cachable_pokemon', map_cells=kwargs['map_cells'])

        if (self.bot.config.mode == "all" or self.bot.config.mode == "poke"):
            self.event_manager.emit_event('cell_work_wild_pokemon', map_cells=kwargs['map_cells'])

        if (self.bot.config.mode == "all" or self.bot.config.mode == "farm") and kwargs['include_fort_on_path']:
            self.event_manager.emit_event('cell_work_forts', map_cells=kwargs['map_cells'], position=kwargs['position'])