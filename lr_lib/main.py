﻿# -*- coding: UTF-8 -*-
# старт классов скрипта
# пример главного запускающего файла lr_start.py:
# from lr_lib.main import init
# if __name__ == '__main__':
# init()

from typing import Iterable, Tuple

import contextlib
import sys

import lr_lib.core.main_core
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.excepthook
import lr_lib.etc.keyb
import lr_lib.etc.logger
import lr_lib.etc.pool.main_pool
import lr_lib.etc.pool.other
import lr_lib.gui.main_gui


def init(excepthook=True, ) -> True:
    """
    инит дополнительных классов, сохр. их в lr_vars, запуск core/gui
    """
    # lr_vars.Logger
    with lr_lib.etc.logger.init() as lr_vars.Logger:
        # lr_vars.MainThreadUpdater
        with lr_lib.etc.pool.other.MainThreadUpdater().init() as lr_vars.MainThreadUpdater:
            # lr_vars.M_POOL, lr_vars.T_POOL
            with lr_lib.etc.pool.main_pool.init() as (lr_vars.M_POOL, lr_vars.T_POOL):
                # core/gui
                exit_code = start(excepthook=excepthook)
    return exit_code


@contextlib.contextmanager
def start(excepthook=True, console_args=sys.argv, ) -> bool:
    """
    запуск core/gui в excepthook обработчике raise
    """
    if excepthook:  # перехват raise -> lr_vars.Logger.error
        lr_vars.Tk.report_callback_exception = lr_lib.etc.excepthook.excepthook

    try:
        exit_code = (as_console, c_args) = main(console_args)
    except Exception as ex:
        lr_lib.etc.excepthook.excepthook(ex)
        raise
    finally:
        lr_vars.Tk.report_callback_exception = lr_vars.original_callback_exception

    i = 'Exit\nas_console={c}\nconsole_args={cas}\nc_args={ca}'
    i = i.format(c=as_console, cas=console_args, ca=c_args, )
    lr_vars.Logger.debug(i)

    exit_code = bool(exit_code)
    return exit_code


def main(console_args: Tuple[str]) -> Tuple[bool, dict]:
    """
    запуск core/gui
    """
    as_console = bool(console_args[1:])
    # core
    c_args = lr_lib.core.main_core.init(as_console=as_console)

    if as_console:  # консольное использование
        lr_lib.core.main_core.start(c_args, echo=True)
    else:  # обычное использование
        with lr_lib.etc.keyb.keyboard_listener():  # hotkey(param from clipboard)
            # gui
            lr_lib.gui.main_gui.init(c_args)
            lr_lib.gui.main_gui.start(action=True, lock=True)

    item = (as_console, c_args)
    return item
