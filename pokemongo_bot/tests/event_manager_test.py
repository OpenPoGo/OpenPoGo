import unittest
from mock import Mock

from pokemongo_bot.event_manager import EventManager, Event
from pokemongo_bot.logger import Logger

class EventManagerTest(unittest.TestCase):
    @staticmethod
    def test_add_listener():
        logger = Mock()
        event_manager = EventManager(logger)

        test_listener = Mock()
        event_manager.add_listener('test', test_listener)

        assert isinstance(event_manager.events['test'], Event)

        assert len(event_manager.events['test'].listeners[0]) == 1

    @staticmethod
    def test_add_listener_priorities():
        logger = Mock()
        event_manager = EventManager(logger)

        test_listener = Mock()
        event_manager.add_listener('test', test_listener, priority=-100)
        event_manager.add_listener('test', test_listener, priority=100)

        assert isinstance(event_manager.events['test'], Event)

        assert len(event_manager.events['test'].listeners[-100]) == 1
        assert len(event_manager.events['test'].listeners[100]) == 1

    @staticmethod
    def test_remove_listener():
        logger = Mock()
        event_manager = EventManager(logger)

        test_listener = Mock()
        event_manager.add_listener('test', test_listener, priority=10)

        assert isinstance(event_manager.events['test'], Event)
        assert len(event_manager.events['test'].listeners) == 1

        event_manager.remove_listener('test', test_listener)

        assert isinstance(event_manager.events['test'], Event)
        assert len(event_manager.events['test'].listeners[10]) == 0

    @staticmethod
    def test_get_registered_events():
        logger = Mock()
        event_manager = EventManager(logger)

        test_listener = Mock()
        event_manager.add_listener('test', test_listener)

        events = event_manager.get_registered_events()

        assert len(events) == 1
        assert 'test' in events

    @staticmethod
    def test_fire():
        logger = Mock()
        event_manager = EventManager(logger)

        # pylint: disable=unused-argument
        def test_listener(value=None):
            return {
                'value': 'first'
            }

        # pylint: disable=unused-argument
        def test_listener_late(value=None):
            return {
                'value': 'second'
            }

        event_manager.add_listener('test', test_listener_late, priority=100)
        event_manager.add_listener('test', test_listener, priority=-100)

        return_data = event_manager.fire('test', value=None)

        assert return_data['value'] == 'second'

    @staticmethod
    def test_fire_cancelled():
        logger = Mock()
        event_manager = EventManager(logger)

        def test_listener():
            return {
                'value': 'first'
            }

        def test_listener_late():
            return False

        event_manager.add_listener('test', test_listener_late, priority=100)
        event_manager.add_listener('test', test_listener, priority=-100)

        return_data = event_manager.fire('test', value=None)

        assert return_data is False

    @staticmethod
    def test_fire_no_listeners():
        import sys
        from io import StringIO

        out = StringIO()
        sys.stdout = out

        logger = Logger()
        event_manager = EventManager(logger)

        event_manager.events['test'] = Event('test', logger)
        event_manager.fire('test', value=None)

        assert 'No handler has registered to handle event "test"' in out.getvalue().strip()

    @staticmethod
    def test_fire_with_context():
        logger = Mock()
        event_manager = EventManager(logger)

        def test_listener(bot=None):
            bot()

        event_manager.add_listener('test', test_listener, priority=-100)

        bot = Mock()
        event_manager.fire_with_context('test', bot)

        bot.assert_called_once()

    @staticmethod
    def test_event_pipeline_empty_output():
        import sys
        from io import StringIO

        out = StringIO()
        sys.stdout = out
        logger = Logger()
        event_manager = EventManager(logger)

        event_manager.events['test'] = Event('test', logger)
        event_manager.events['test'].listeners['test_listener'] = []
        event_manager.print_all_event_pipelines()

        assert 'Event pipeline for "test" is empty.' in out.getvalue().strip()

    @staticmethod
    def test_event_pipeline_no_listeners():
        import sys
        from io import StringIO

        out = StringIO()
        sys.stdout = out
        logger = Logger()
        event_manager = EventManager(logger)

        event_manager.events['test'] = Event('test', logger)
        event_manager.events['test'].listeners['test_listener'] = []
        event_manager.print_all_event_pipelines()

        assert 'Event pipeline for "test" is empty.' in out.getvalue().strip()

    @staticmethod
    def test_event_pipeline_output():
        import sys
        from io import StringIO

        out = StringIO()
        sys.stdout = out

        logger = Logger()
        event_manager = EventManager(logger)

        def test_listener_1(bot=None):
            bot()

        def test_listener_2(bot=None):
            bot()

        def test_listener_3(bot=None):
            bot()

        def test_listener_4(bot=None):
            bot()

        event_manager.add_listener('test1', test_listener_1, priority=-100)
        event_manager.add_listener('test1', test_listener_2, priority=0)
        event_manager.add_listener('test1', test_listener_3, priority=0)
        event_manager.add_listener('test1', test_listener_4, priority=100)
        event_manager.add_listener('test2', test_listener_1, priority=100)
        event_manager.print_all_event_pipelines()

        assert 'Event pipeline for "test1":' in out.getvalue().strip()
        assert '-100 (test_listener_1) -> 0 (test_listener_2 -> test_listener_3) -> 100 (test_listener_4)' in out.getvalue().strip()
        assert 'Event pipeline for "test2":' in out.getvalue().strip()
        assert '100 (test_listener_1)' in out.getvalue().strip()
