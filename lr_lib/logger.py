# -*- coding: UTF-8 -*-
# вывод сообщений, обработка исключений

import os
import sys
import time
import queue
import tempfile
import subprocess
import traceback
import functools
import logging, logging.handlers
from tkinter import messagebox

from lr_lib import (
    defaults,
)


if not os.path.isdir(defaults.logPath):
    os.makedirs(defaults.logPath)  # каталог лога

formatter = u'\n[ %(levelname)s ]: %(filename)s %(funcName)s:%(lineno)d %(threadName)s %(asctime)s.%(msecs)d \n%(message)s'


class SessionStateHandler(logging.Handler):
    '''перенаправление logging в Window'''
    def emit(self, record: logging) -> None:
        if defaults.Window:
            defaults.Window.print(record.levelname, self.format(record))


Logger = logging.getLogger('__main__')
Logger.setLevel(defaults.logger_level)

consoleHandler = logging.StreamHandler()  # консоль
sessionHandler = SessionStateHandler()  # gui
logHandler = logging.FileHandler(defaults.logFullName, defaults.log_overdrive, encoding='cp1251')

LoggerQueue = queue.Queue()
LoggerQueueListener = logging.handlers.QueueHandler(LoggerQueue)
Logger_listener = logging.handlers.QueueListener(LoggerQueue, sessionHandler, consoleHandler, logHandler)

Logger.addHandler(LoggerQueueListener)


def openTextInEditor(text: str) -> None:
    '''открытие сообщения в Блокноте'''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        with open(f.name, 'w', errors='replace') as tf:
            tf.write(text)
        subprocess.Popen([defaults.EDITOR['exe'], f.name])
        f.close()


def loggingLevelCreator(level_num: int, level: str) -> None:
    ''' создать/переопределить новый level/exception для logging -> Logger'''
    logging.addLevelName(level_num, level.upper())
    level = level.lower()

    def logging_level(self, message, *args, error_state=('critical', 'error', 'warning', ), **kwargs) -> None:
        '''переопределенный logging метод'''
        if self.isEnabledFor(level_num):
            if kwargs.pop('notepad', None):
                openTextInEditor(message)
            parent = kwargs.pop('parent', None)

            self._log(level_num, message, args, **kwargs)  # оригинальный logging метод

            if level in error_state:
                if (parent is None) and defaults.Window and defaults.Window.action_windows:  # сделать action родителем
                    parent = defaults.Window.action_windows[next(iter(defaults.Window.action_windows))]
                message = '{s}\n{m}\n{s}'.format(m=message, s=defaults.PRINT_SEPARATOR)
                if defaults.VarShowPopupWindow.get():  # окно с ошибкой
                    if level == 'warning':
                        messagebox.showwarning(level.capitalize(), message, parent=parent)
                    else:
                        messagebox.showerror(level.upper(), message, parent=parent)
    # создать
    logging_level.__name__ = level
    setattr(logging.getLoggerClass(), level, logging_level)


for level in defaults.loggingLevels:  # создать logging.level
    loggingLevelCreator(defaults.loggingLevels[level], level)


def set_formatter(handler: logging.handlers, formatter=formatter, datefmt="%H:%M:%S") -> None:
    '''logging.Formatter'''
    handler.setFormatter(logging.Formatter(formatter, datefmt=datefmt))


for handler in (logHandler, consoleHandler, sessionHandler,):
    set_formatter(handler)


def excepthook(*args) -> None:
    """обработка raise: сокращенный стектрейс + исходный код"""
    len_args = len(args)
    if len_args == 1:
        exc_type, exc_val, exc_tb = type(args[0]), args[0], args[0].__traceback__
    elif len_args == 3:
        exc_type, exc_val, exc_tb = args
    else:
        exc_type, exc_val, exc_tb = sys.exc_info()

    traceback.print_tb(exc_tb)
    full_tb_write(exc_type, exc_val, exc_tb)

    ern = exc_type.__name__
    if defaults.Window:
        defaults.Window.err_to_widgts(exc_type, exc_val, exc_tb, ern)
    Logger.critical(get_tb(exc_type, exc_val, exc_tb, ern))


def full_tb_write(exc_type, exc_val, exc_tb) -> None:
    '''логировать полный traceback'''
    with open(defaults.logFullName, 'a') as log:
        log.write('\n{0}\n\t>>> traceback.print_tb\n{0}\n'.format(defaults.PRINT_SEPARATOR))
        traceback.print_tb(exc_tb, file=log)
        log.write('{t}\n{v}'.format(t=exc_type, v=exc_val))
        log.write('\n{0}\n\t<<< traceback.print_tb\n{0}\n'.format(defaults.PRINT_SEPARATOR))


def get_tb(exc_type, exc_val, exc_tb, err_name: str) -> str:
    '''traceback + исходный код'''
    if not exc_tb:
        return '{} {} {}'.format(exc_type, exc_val, exc_tb)
    exc_lines = traceback.format_exception(exc_type, exc_val, exc_tb)

    def get_code() -> str:
        '''исходный код'''
        for line in reversed(exc_lines):
            if '\lr_lib\\' in line:
                break
        try:
            fileName = line.split('"')[1]
            lineNum = int(line.split(',')[1].split('line')[-1])
            with open(fileName, errors='replace', encoding='utf-8') as file:
                text = file.read().split('\n')

            left = []
            for line in reversed(text[:lineNum]):
                if line.strip():
                    left.append(line)
                    if len(left) == defaults.EHOME:
                        break
            _, f = os.path.split(fileName)
            left[0] = '\n!!! {e} [ {f} : строка {l} ]\n{line}\n'.format(e=err_name, line=left[0], f=f, l=lineNum)
            left.reverse()

            right = []
            for line in text[lineNum:]:
                if line.strip():
                    right.append(line)
                    if len(right) == defaults.EEND:
                        break

            code = '{l}\n{r}'.format(l='\n'.join(left), r='\n'.join(right))
            return code
        except Exception as ex:
            return 'неудалось загрузить код файла\n{}'.format(ex)

    tb = ''.join(exc_lines[-1:]).rstrip()
    code = get_code().rstrip()
    return '{tb}\n{s}\n{code}'.format(tb=tb, code=code, s=defaults.PRINT_SEPARATOR)


def exec_time(func: callable) -> callable:
    '''время выполнения func'''
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        t = time.time()
        out = func(*args, **kwargs)
        t = time.time() - t
        Logger.trace('<- {t} сек: {f}'.format(f=func, t=round(t, 1)))
        return out
    return wrap
