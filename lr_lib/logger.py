# -*- coding: UTF-8 -*-
# вывод сообщений, обработка исключений

import os
import queue
import contextlib
import logging, logging.handlers
from tkinter import messagebox

from lr_lib import (
    defaults,
    other as lr_other,
)

formatter = u'\n[ %(levelname)s ]: %(filename)s %(funcName)s:%(lineno)d %(threadName)s %(asctime)s.%(msecs)d \n%(message)s'
datefmt = "%H:%M:%S"


class GuiHandler(logging.Handler):
    '''logging в Window'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(formatter, datefmt=datefmt))

    def emit(self, record: logging) -> None:
        if defaults.Window:
            defaults.Window.print(record.levelname, self.format(record))


class ConsoleHandler(logging.StreamHandler):
    '''logging в Console'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(formatter, datefmt=datefmt))


class LogHandler(logging.FileHandler):
    '''logging в лог'''
    if not os.path.isdir(defaults.logPath):
        os.makedirs(defaults.logPath)  # создать каталог лога

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(formatter, datefmt=datefmt))


def loggingLevelCreator(level_num: int, level: str) -> None:
    ''' создать/переопределить новый level-exception, для *Handler.level -> logging.level'''
    logging.addLevelName(level_num, level.upper())
    level = level.lower()

    def logging_level(self, message, *args, **kwargs) -> None:
        '''переопределенный logging метод'''
        if self.isEnabledFor(level_num):
            notepad = kwargs.pop('notepad', None)
            parent = kwargs.pop('parent', None)

            self._log(level_num, message, args, **kwargs)  # оригинальный logging метод

            if notepad:
                lr_other.openTextInEditor(message)
            # окно с ошибкой
            if defaults.VarShowPopupWindow.get() and (level in ('critical', 'error', 'warning',)):
                if (parent is None) and defaults.Window:  # сделать action родителем
                    parent = defaults.Window.get_main_action()

                message = '{s}\n{m}\n{s}'.format(m=message, s=defaults.PRINT_SEPARATOR)
                if level == 'warning':
                    messagebox.showwarning(level.capitalize(), message, parent=parent)
                else:
                    messagebox.showerror(level.upper(), message, parent=parent)

    logging_level.__name__ = level
    setattr(logging.getLoggerClass(), level, logging_level)  # создать


@contextlib.contextmanager
def Logger_Creator() -> iter((None,)):
    '''слушатель QueueHandler: Logger_listener.start() / Logger_listener.stop()'''
    for level in defaults.loggingLevels:  # создать logging.level
        loggingLevelCreator(defaults.loggingLevels[level], level)

    defaults.Logger = logging.getLogger('__main__')
    defaults.Logger.setLevel(defaults.logger_level)

    LoggerQueue = queue.Queue()
    LoggerQueueListener = logging.handlers.QueueHandler(LoggerQueue)
    defaults.Logger.addHandler(LoggerQueueListener)

    listener = logging.handlers.QueueListener(LoggerQueue, GuiHandler(), ConsoleHandler(), LogHandler(defaults.logFullName, defaults.log_overdrive, encoding='cp1251'))
    try:
        yield listener.start()
    except Exception:
        raise
    else:
        listener.stop()
        logging.shutdown()
