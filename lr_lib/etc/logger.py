# -*- coding: UTF-8 -*-
# вывод сообщений

import contextlib
import logging
import logging.handlers
import os
import queue
from tkinter import messagebox
from typing import Iterable

import lr_lib
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars as lr_vars
from lr_lib.etc.sysinfo import system_info

Fmt = u'[ %(levelname)s ]: %(filename)s %(funcName)s:%(lineno)d %(threadName)s %(asctime)s.%(msecs)d \n%(message)s'
DateFmt = "%H:%M:%S"


class GuiHandler(logging.Handler):
    """
    logging в Window
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(Fmt, datefmt=DateFmt))
        return

    def emit(self, record: logging) -> None:
        """
        вывод сообщения
        """
        if lr_vars.Window and lr_vars.MainThreadUpdater:
            lr_vars.Window.print(record.levelname, self.format(record))
        return


class ConsoleHandler(logging.StreamHandler):
    """
    logging в Console
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(Fmt, datefmt=DateFmt))
        return


class LogHandler(logging.FileHandler):
    """
    logging в лог
    """
    if not os.path.isdir(lr_vars.logPath):
        os.makedirs(lr_vars.logPath)  # создать каталог лога

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter(Fmt, datefmt=DateFmt))
        return


def _LoggerLevelCreator(level_num: int, level: str) -> None:
    """
    создать/переопределить новый level-exception, для *Handler.level -> logging.level
    """
    logging.addLevelName(level_num, level.upper())
    level = level.lower()

    def logging_level(self, message, *args, **kwargs) -> None:
        """
        переопределенный logging метод
        """
        if self.isEnabledFor(level_num):
            notepad = kwargs.pop('notepad', None)
            parent = kwargs.pop('parent', None)
            log = kwargs.pop('log', True)

            if log:
                self._log(level_num, message, args, **kwargs)  # оригинальный logging метод

            if notepad:
                lr_lib.core.etc.other.openTextInEditor(message)
            # окно с ошибкой
            if lr_vars.VarShowPopupWindow.get() and (level in ('critical', 'error', 'warning',)):
                if (parent is None) and lr_vars.Window:  # сделать action родителем
                    parent = lr_vars.Window.get_main_action()

                message = '{s}\n{m}\n{s}'.format(m=message, s=lr_vars.SEP)
                if level == 'warning':
                    messagebox.showwarning(level.capitalize(), message, parent=parent)
                else:
                    messagebox.showerror(level.upper(), message, parent=parent)
        return

    logging_level.__name__ = level
    setattr(logging.getLoggerClass(), level, logging_level)  # создать
    return


def LoggerLevelCreator(levels: {str: int}) -> None:
    """
    создать logging.level
    """
    for level in levels:
        _LoggerLevelCreator(levels[level], level)
        continue
    return


@contextlib.contextmanager
def init(
        name='__main__',
        encoding='cp1251',
        levels=lr_lib.core.var.etc.vars_other.loggingLevels,
) -> Iterable[logging.getLogger]:
    """
    инит логера с выводом в потоке
    """
    LoggerLevelCreator(levels)

    (Logger, listener) = LoggerCreator(name, encoding=encoding)
    try:
        listener.start()

        i = 'version={v}, defaults.VarEncode={ce}\n{si}'
        i = i.format(v=lr_vars.VERSION, ce=lr_lib.core.var.etc.vars_other.VarEncode.get(), si=system_info(), )
        Logger.info(i)

        yield Logger
    except Exception:
        raise
    else:
        listener.stop()
        logging.shutdown()
    return


def LoggerCreator(name: str, encoding: str) -> tuple:
    """
    создать Logger и QueueHandler
    """
    LoggerQueue = queue.Queue()
    LoggerQueueListener = logging.handlers.QueueHandler(LoggerQueue)

    Logger = logging.getLogger(name)
    Logger.setLevel(lr_vars.logger_level)
    Logger.addHandler(LoggerQueueListener)

    listener = logging.handlers.QueueListener(
        LoggerQueue,
        GuiHandler(),
        ConsoleHandler(),
        LogHandler(lr_vars.logFullName, lr_vars.log_overdrive, encoding=encoding),
    )

    it = (Logger, listener)
    return it
