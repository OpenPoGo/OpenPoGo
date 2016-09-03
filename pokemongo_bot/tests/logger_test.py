from __future__ import print_function
import unittest

from mock import Mock

import pokemongo_bot
from pokemongo_bot import EventManager
from pokemongo_bot import Logger


class LoggerTest(unittest.TestCase):
    @staticmethod
    def test_debug_by_call():
        import sys
        from io import StringIO
        out = StringIO()
        sys.stdout = out

        logger = Logger().getLogger('test')

        logger.debug("log row", color="yellow")
        output = out.getvalue().strip()
        assert "[test] log row" in output

    @staticmethod
    def test_info_by_call():
        import sys
        from io import StringIO
        out = StringIO()
        sys.stdout = out

        logger = Logger().getLogger('test')

        logger.info("log row", color="yellow")
        output = out.getvalue().strip()
        assert "[test] log row" in output

    @staticmethod
    def test_warning_by_call():
        import sys
        from io import StringIO
        out = StringIO()
        sys.stdout = out

        logger = Logger().getLogger('test')

        logger.warning("log row", color="yellow")
        output = out.getvalue().strip()
        assert "[test] log row" in output

    @staticmethod
    def test_error_by_call():
        import sys
        from io import StringIO
        out = StringIO()
        sys.stdout = out

        logger = Logger().getLogger('test')

        logger.error("log row", color="yellow")
        output = out.getvalue().strip()
        assert "[test] log row" in output

    @staticmethod
    def test_critical_by_call():
        import sys
        from io import StringIO
        out = StringIO()
        sys.stdout = out

        logger = Logger().getLogger('test')

        logger.critical("log row", color="yellow")
        output = out.getvalue().strip()
        assert "[test] log row" in output
