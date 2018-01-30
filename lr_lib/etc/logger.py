# -*- coding: UTF-8 -*-
# вывод сообщений

import os
import queue
import contextlib
import logging
import logging.handlers

from tkinter import messagebox

import lr_lib.core.etc.other as lr_other
import lr_lib.core.var.vars as lr_vars


formatter = u'\n[ %(levelname)s ]: %(filename)s %(funcName)s:%(lineno)d %(threadName)s %(asctime)s.%(msecs)d \n%(message)s'
datefmt = "%H:%M:%S"


class GuiHandler(logging.Handler):
    '''logging в Window'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(formatter, datefmt=datefmt))

    def emit(self, record: logging) -> None:
        if lr_vars.Window and lr_vars.MainThreadUpdater:
            lr_vars.Window.print(record.levelname, self.format(record))


class ConsoleHandler(logging.StreamHandler):
    '''logging в Console'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(formatter, datefmt=datefmt))


class LogHandler(logging.FileHandler):
    '''logging в лог'''
    if not os.path.isdir(lr_vars.logPath):
        os.makedirs(lr_vars.logPath)  # создать каталог лога

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(formatter, datefmt=datefmt))


def _LoggerLevelCreator(level_num: int, level: str) -> None:
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
            if lr_vars.VarShowPopupWindow.get() and (level in ('critical', 'error', 'warning',)):
                if (parent is None) and lr_vars.Window:  # сделать action родителем
                    parent = lr_vars.Window.get_main_action()

                message = '{s}\n{m}\n{s}'.format(m=message, s=lr_vars.PRINT_SEPARATOR)
                if level == 'warning':
                    messagebox.showwarning(level.capitalize(), message, parent=parent)
                else:
                    messagebox.showerror(level.upper(), message, parent=parent)

    logging_level.__name__ = level
    setattr(logging.getLoggerClass(), level, logging_level)  # создать


def LoggerLevelCreator(levels: {str: int}) -> None:
    '''создать logging.level'''
    for level in levels:
        _LoggerLevelCreator(levels[level], level)


@contextlib.contextmanager
def init(name='__main__', encoding='cp1251', levels=lr_vars.loggingLevels) -> iter((logging.getLogger,)):
    LoggerLevelCreator(levels)

    (Logger, listener) = LoggerCreator(name, encoding=encoding)
    try:
        listener.start()
        yield Logger
    except Exception:
        raise
    else:
        listener.stop()
        logging.shutdown()


def LoggerCreator(name: str, encoding: str) -> logging.getLogger:
    '''создать Logger и QueueHandler'''
    LoggerQueue = queue.Queue()
    LoggerQueueListener = logging.handlers.QueueHandler(LoggerQueue)

    Logger = logging.getLogger(name)
    Logger.setLevel(lr_vars.logger_level)
    Logger.addHandler(LoggerQueueListener)

    listener = logging.handlers.QueueListener(
        LoggerQueue, GuiHandler(), ConsoleHandler(), LogHandler(lr_vars.logFullName, lr_vars.log_overdrive, encoding=encoding))

    return (Logger, listener)