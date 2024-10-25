import logging
import re
from functools import partialmethod
from logging.handlers import WatchedFileHandler
from datetime import datetime
from os import makedirs
import coloredlogs
from utils.SteelSeriesLoggerHandler import SteelSeriesHandler, SsFormatter


class ColorFormatter(coloredlogs.ColoredFormatter):
    def __init__(self, fmt):
        super().__init__(fmt=fmt, style="{")

    def format(self, record):
        message = super().format(record)
        # Replace a specific character, e.g., '1', with a blue colored version
        message = message.replace('1', '\033[94m1\033[0m')  # Blue color
        return message

class MyLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def addLevel(cls, name, lvl, style):
        """Don't forget to call self.install() afterwards if you wish to add colored levels after mylogger.init()"""
        setattr(cls, name.lower(), partialmethod(cls._anyLog, lvl))
        logging.addLevelName(lvl, name)
        coloredlogs.DEFAULT_LEVEL_STYLES.update({name.lower(): style})

    def _anyLog(self, level, message, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, message, args, **kwargs)

    def __call__(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, message, args, **kwargs)

    def install(self):
        """if you wish to add more colored levels, call this after calling logger.addLevel()"""
        coloredlogs.install(level=self.getEffectiveLevel(), logger=self, fmt=FORMAT, style="{")


# formatting the colorlogger
# fmt = "[ %(asctime)s %(name)s (%(filename)s) %(lineno)d %(funcName)s() %(levelname)s ] %(message)s"
FORMAT = "[ {asctime} {name} {filename} {lineno} {funcName}() {levelname} ] {message}"
coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 100}, 'lineno': {'color': 'magenta'}, 'levelname': {'bold': True, 'color': 'black'}, 'filename': {'color': 25}, 'name': {'color': 'blue'}, 'funcname': {'color': 'cyan'}}
coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'bold': True, 'color': 'red'}, 'debug': {'bold': True, 'color': 'black'}, 'error': {'color': 'red'}, 'info': {'color': 'green'}, 'notice': {'color': 'magenta'}, 'spam': {'color': 'green', 'faint': True}, 'success': {'bold': True, 'color': 'green'}, 'verbose': {'color': 'blue'}, 'warning': {'color': 'yellow'}}

logging.setLoggerClass(MyLogger)
baselogger: MyLogger = logging.getLogger("main")
baselogger.addLevel("Event", 25, {"color": "white"})
baselogger.addLevel("React", 19, {"color": "white"})
baselogger.addLevel("Highlight", 51, {"color": "magenta", "bold": True})
# baselogger.addLevel("Blue", 23, {"color": 25})
# baselogger.addLevel("Gold", 22, {"color": 214})
# https://coloredlogs.readthedocs.io/en/latest/api.html#available-text-styles-and-colors


def init(args=None):
    #
    # sse = SteelSeriesHandler(name="svvi")
    # sse.setLevel(logging.INFO)
    #
    # ssf = SsFormatter(flash_freq=2, n_flashes=2, display_time=2000)
    # sse.setFormatter(ssf)
    #
    # baselogger.addHandler(sse)

    baselogger.setLevel(logging.DEBUG)  # base is debug, so the file handler could catch debug msgs too
    if args and args.debug:
        coloredlogs.install(level=logging.DEBUG, logger=baselogger, fmt=FORMAT, style="{")
    else:
        coloredlogs.install(level=logging.INFO, logger=baselogger, fmt=FORMAT, style="{")


    # handler = baselogger.handlers[1]
    for h in baselogger.handlers:
        if isinstance(h, coloredlogs.StandardErrorHandler):
            handler = h
            break
    else:
        return baselogger

    existing_formatter = handler.formatter
    if existing_formatter:
        class InheritedFormatter(existing_formatter.__class__):

            def __init__(self, fmt):
                super().__init__(style="{", fmt=fmt)
            def format(self, record):
                message = super().format(record)
                message = re.sub(r'(?<=\[|\s)1(?=,|\s|\])', '\033[31m1\033[32m', message)  # Blue color
                message = message.replace("array([[", "array([\n       [")
                return message

        handler.setFormatter(InheritedFormatter(existing_formatter._fmt))

    # sh = logging.StreamHandler()
    # sh.setFormatter(ColorFormatter("[ {asctime} {name} {filename} {lineno} {funcName}() {levelname} ] {message}"))
    # baselogger.addHandler(sh)
    return baselogger
