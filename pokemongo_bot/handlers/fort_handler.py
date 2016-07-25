# -*- coding: utf-8 -*-

from cell_workers import SeenFortWorker
from cell_workers.utils import filtered_forts, distance
from events import IEventHandler

class FortHandler(IEventHandler):
    handles = 'cell_work_forts'

    def process(self, **kwargs):
    	(lat, lng, alt) = kwargs['position']
        forts = filtered_forts(lat, lng, sum([cell.get("forts", []) for cell in kwargs['map_cells']], []))
        if forts:
            worker = SeenFortWorker(forts[0], self.bot)
            hack_chain = worker.work()