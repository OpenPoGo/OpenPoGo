# pylint: disable=redefined-builtin
from __future__ import print_function
from builtins import str
import atexit
import time
import os

from colorama import Fore, Back, Style
from pokemongo_bot.event_manager import manager

# Uncomment for type annotations on Python 3
# from typing import Optional


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


make_sure_path_exists("logs")
output_file = open(os.path.join("logs", "{}.txt".format(time.strftime("%Y.%m.%d-%H.%M.%S"))), "w")
atexit.register(output_file.close)


def log(string, color="black", prefix=None, fire_event=True):
    # type: (str, Optional[str], Optional[str], Optional[bool]) -> None
    if fire_event:
        manager.fire("logging", text=string, color=color, prefix=prefix)
    else:
        _log(text=string, color=color, prefix=prefix)


@manager.on("logging")
def _log(text="", color="black", prefix=None):
    # type: (str, Optional[str], Optional[str]) -> None
    color_hex = {
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'red': Fore.RED
    }
    string = str(text)
    output = u"[" + time.strftime("%Y-%m-%d %H:%M:%S") + u"] "
    if prefix is not None:
        output += u"[{}] ".format(str(prefix))
    output += string
    output_file.write(output + "\n")
    if color in color_hex:
        output = color_hex[color] + output + Style.RESET_ALL
    print(output)
