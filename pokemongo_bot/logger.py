# pylint: disable=redefined-builtin
from __future__ import print_function
from builtins import str

# --
# Python Dependencies
# --
import logging
from logging.handlers import TimedRotatingFileHandler
import copy
import os
import sys
import time
import inspect

# --
# Project Dependencies
# --
from app import kernel
from pokemongo_bot.event_manager import EventManager

# --
# Remote Dependencies
# --
import colorlog
from colorlog import ColoredFormatter
from colorlog.escape_codes import escape_codes, parse_colors

# --
# Logger
# --
@kernel.container.register('logger', ['@config.core'])
class Logger(object):
    event_manager = None

    def __init__(self, config=None):
        self.config = config
        self.log_prefix = None

        # init logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        # UnitTest Running? Write to STDOUT without colors for Assertions
        if self.is_test():
            handlerStream = logging.StreamHandler(sys.stdout)
            handlerStream.setLevel(logging.DEBUG)
            handlerStream.setFormatter(logging.Formatter(u"[%(asctime)s] %(levelname)-8s [%(prefix)-s] %(message)s"))
            self._logger.addHandler(handlerStream)

        # Handler: Console [ColorLog] - Supress on UnitTest to prevent log spamming
        if self.is_test() is False:
            handlerConsole = colorlog.StreamHandler()
            handlerConsole.setLevel(logging.DEBUG)
            handlerConsole.setFormatter(ColoredFormatter(
                u"[%(asctime)s] %(log_color)s%(levelname)-8s%(reset)s [%(prefix)-s] %(message_color)s%(message)s",
                datefmt='%Y-%m-%d %H:%M:%S',
                reset=True,
                log_colors={
                    'DEBUG':    'cyan',
                    'INFO':     'green',
                    'WARNING':  'yellow',
                    'ERROR':    'red',
                    'CRITICAL': 'red,bg_white',
                },
                secondary_log_colors={
                    'message': {
                        'ERROR':    'red',
                        'CRITICAL': 'red'
                    }
                },
                style='%'
            ))
            self._logger.addHandler(handlerConsole)

        # Config Deprecated?
        if self.config is not None and 'logging' not in self.config.keys():
            self.error("Configuration Deprecated: Please see config.yml.example to add the logging sector!", "red")

        # Handler: File
        if self.config is not None and 'logging' in self.config.keys() and self.config['logging']['log_to_file']:
            log_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), self.config['logging']['log_directory'])
            log_directory_custom = None

            # default dir
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
                self.info('Created missing log directory [{}]'.format(log_directory))
            log_path = log_directory
            # custom dir
            if self.config['logging']['log_directory_individual'] is not None:
                log_directory_custom = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), self.config['logging']['log_directory'], self.config['logging']['log_directory_individual'])
                if not os.path.exists(log_directory_custom):
                    os.makedirs(log_directory_custom)
                    self.info('Created missing individual log directory [{}]'.format(log_directory_custom))
                log_path = log_directory_custom

            # user defined filename
            log_filename = self.config['logging']['file_name']

            # log rotation every minute
            handlerFile = TimedRotatingFileHandler(os.path.join(log_path, 'pgolog'), when='MIDNIGHT')
            handlerFile.suffix = log_filename
            handlerFile.setLevel(logging.DEBUG)
            handlerFile.setFormatter(logging.Formatter(u"[%(asctime)s] %(levelname)-8s [%(prefix)-s] %(message)s"))
            self._logger.addHandler(handlerFile)

    def getLogger(self, prefix=None):
        loggerInstance = copy.copy(self)
        loggerInstance.log_prefix = prefix

        return loggerInstance

    def debug(self, message, color=None):
        message_color = self._get_colorcode(color)
        logger_adapter = self.setup_logadapter(self.log_prefix, message_color)
        logger_adapter.debug(message)

    def info(self, message, color=None):
        message_color = self._get_colorcode(color)
        logger_adapter = self.setup_logadapter(self.log_prefix, message_color)
        logger_adapter.info(message)

    def warning(self, message, color=None):
        message_color = self._get_colorcode(color)
        logger_adapter = self.setup_logadapter(self.log_prefix, message_color)
        logger_adapter.warning(message)

    def error(self, message, color=None):
        message_color = self._get_colorcode(color)
        logger_adapter = self.setup_logadapter(self.log_prefix, message_color)
        logger_adapter.error(message)

    def critical(self, message, color=None):
        message_color = self._get_colorcode(color)
        logger_adapter = self.setup_logadapter(self.log_prefix, message_color)
        logger_adapter.critical(message)

    def setup_logadapter(self, prefix=None, messageColor=""):
        if prefix is None:
            prefix = 'Bot'

        # logger data
        logger_extra = {
            'prefix': prefix,
            'message_color': messageColor
        }

        return logging.LoggerAdapter(self._logger, logger_extra)

    @staticmethod
    def _get_colorcode(color):
        if color is None:
            return ""
        # all valid colors
        elif color not in {"black", "red", "green", "yellow", "blue", "purple", "cyan", "white", "reset"}:
            return ""
        else:
            return parse_colors(color)

    # EventManager
    def setEventManager(self, event_manager):
        self.event_manager = event_manager

    # Check for UnitTest
    # Credits to http://stackoverflow.com/users/3803152/thesounddefense
    @staticmethod
    def is_test():
        current_stack = inspect.stack()
        for stack_frame in current_stack:
            # returns None when running the tests
            if stack_frame[4] is None:
                return True
        return False
