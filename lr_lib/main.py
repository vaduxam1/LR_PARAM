# -*- coding: UTF-8 -*-
# старт классов скрипта
# пример главного запускающего файла lr_start.py:
# from lr_lib.main import init
# if __name__ == '__main__':
# init()

from typing import Iterable, Tuple

import sys

import lr_lib.core.main_core
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.excepthook
# import lr_lib.etc.keyb
import lr_lib.etc.logger
import lr_lib.etc.pool.main_pool
import lr_lib.etc.pool.other
import lr_lib.gui.main_gui


def init(**kwargs) -> True:
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
                exit_state = start(**kwargs)
    return exit_state


def start(excepthook=True, console_args=sys.argv) -> bool:
    """
    запуск core/gui в excepthook обработчике raise
    """
    if excepthook:  # перехват raise -> lr_vars.Logger.error
        lr_vars.Tk.report_callback_exception = lr_lib.etc.excepthook.excepthook

    try:
        item = (as_console, c_args) = main(console_args)
    except Exception as ex:
        lr_lib.etc.excepthook.excepthook(ex)
        raise
    finally:
        lr_vars.Tk.report_callback_exception = lr_vars.original_callback_exception

    i = 'Exit\nas_console={c}\nconsole_args={cas}\nc_args={ca}'
    i = i.format(c=as_console, cas=console_args, ca=c_args, )
    lr_vars.Logger.debug(i)

    exit_state = bool(item)  # True
    return exit_state


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
        # with lr_lib.etc.keyb.keyboard_listener():  # hotkey(param from clipboard)
        # gui
        lr_lib.gui.main_gui.init(c_args)
        # блокировать главный поток
        lr_lib.gui.main_gui.start()

    item = (as_console, c_args)
    return item


def _test():
    import lr_lib._next_34
    lr_vars.VarParam.set('lYKQ1b0')
    alv = list(lr_lib._next_34.all_wrsp_variant())
    import json
    print(json.dumps(alv, ensure_ascii=False, indent=2))
    return
