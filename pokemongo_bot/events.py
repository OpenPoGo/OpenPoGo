# -*- coding: utf-8 -*-

class EventManager(object):

    def __init__(self, bot):
        self.bot = bot
        self.event_handle_dict = {}
        self._init_event_handlers()

    def _init_event_handlers(self):
        pass

    def register_handler(self, event, handler_class):
        handler_list = self.event_handle_dict.get(event, [])
        handler_list += handler_class

    def emit_event(self, event_name, **kwargs):
        handlers = self.event_handle_dict.get(event_name, [])

        for handler in handlers:
            handler_object = handler(self, **kwargs)
            handler_object.process()

class IEventHandler(object):

    def __init__(self, bot, event_manager):
        self.bot = bot
        self.event_manager = event_manager
        self.event_manager.register_handler(self.handles, self)

    def process(self, **kwargs):
        pass
