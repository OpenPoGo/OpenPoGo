from __future__ import print_function
import inspect


class Event(object):
    def __init__(self, name):
        self.name = name
        self.listeners = {}
        self.num_listeners = 0
        print("[Event Manager] Initialized new event \"{}\"".format(self.name))

    def add_listener(self, listener, priority=0):
        self.num_listeners += 1
        if priority not in self.listeners:
            self.listeners[priority] = set()
        self.listeners[priority].add(listener)

    def remove_listener(self, listener):
        for priority in self.listeners:
            self.listeners[priority].discard(listener)
        self.num_listeners -= 1

    def fire(self, **kwargs):
        if self.num_listeners == 0:
            print("[Event Manager] WARNING: No handler has registered to handle event \"{}\"".format(self.name))

        # Sort events by priorities from greatest to least
        priorities = sorted(self.listeners, key=lambda event_priority: event_priority * -1)
        for priority in priorities:
            for listener in self.listeners[priority]:

                # Pass in the event name to the handler
                kwargs["event_name"] = self.name

                # Slice off any named arguments that the handler doesn't need
                # pylint: disable=deprecated-method
                argspec = inspect.getargspec(listener)

                if not argspec.args:
                    return_dict = listener()
                else:
                    listener_args = {}
                    for key in argspec.args:
                        listener_args[key] = kwargs.get(key)
                    return_dict = listener(**listener_args)

                # Update the list of arguments to be used for the next function
                # This enables "pipeline"-like functionality - if arguments to an event handler
                # need to be processed in some way, another handler with higher priority can be
                # installed beforehand to do this without touching the original handler.
                if return_dict is not None:
                    kwargs.update(return_dict)
        return kwargs


class EventManager(object):
    def __init__(self):
        self.events = {}

    def add_listener(self, name, listener, **kwargs):
        if name not in self.events:
            self.events[name] = Event(name)
        priority = kwargs.get("priority", 0)
        self.events[name].add_listener(listener, priority)

    # Decorator for event handlers.
    # Higher priority events run before lower priority ones.
    # pylint: disable=invalid-name
    def on(self, *trigger_list, **kwargs):
        priority = kwargs.get("priority", 0)

        def register_handler(function):
            for trigger in trigger_list:
                self.add_listener(trigger, function, priority=priority)
            return function

        return register_handler

    # Fire an event and call all event handlers.
    def fire(self, event_name, *args, **kwargs):
        if event_name in self.events:
            return self.events[event_name].fire(*args, **kwargs)

    # Fire an event and call all event handlers, injecting the bot context as a named parameter.
    def fire_with_context(self, event_name, bot, *args, **kwargs):
        if event_name in self.events:
            kwargs['bot'] = bot
            return self.fire(event_name, *args, **kwargs)

    def remove_listener(self, name, listener):
        if name in self.events:
            self.events[name].remove_listener(listener)


# This will only be loaded once
# To use, add the following code to plugins:
# from event_manager import manager
# pylint: disable=invalid-name
manager = EventManager()
