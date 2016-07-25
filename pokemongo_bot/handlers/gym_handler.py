# -*- coding: utf-8 -*-

from events import IEventHandler

class GymHandler(IEventHandler):
    handles = 'cell_work_gyms'

    def process(self, **kwargs):
    	pass