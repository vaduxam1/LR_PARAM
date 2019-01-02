# -*- coding: UTF-8 -*-
# старт классов скрипта
# пример главного запускающего файла lr_start.py:
# from lr_lib.main import init
# if __name__ == '__main__':
    # init()

import sys
import contextlib

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_f

import lr_lib.gui.main_gui
import lr_lib.core.main_core
import lr_lib.etc.logger
import lr_lib.etc.sysinfo
import lr_lib.etc.excepthook
import lr_lib.etc.keyb
import lr_lib.etc.pool.main_pool
import lr_lib.etc.pool.other


def init(excepthook=True):
    """инит дополнительных классов, сохр. их в lr_vars, запуск core/gui"""
    # lr_vars.Logger
    with lr_lib.etc.logger.init(name='__main__', encoding='cp1251', levels=lr_lib.core.var.vars_f.loggingLevels) as lr_vars.Logger:
        lr_vars.Logger.info('version={v}, defaults.VarEncode={ce}\n{si}'.format(
            v=lr_vars.VERSION, ce=lr_lib.core.var.vars_f.VarEncode.get(), si=lr_lib.etc.sysinfo.system_info()))

        # lr_vars.MainThreadUpdater
        with lr_lib.etc.pool.other.MainThreadUpdater().init() as lr_vars.MainThreadUpdater:
            # lr_vars.M_POOL, lr_vars.T_POOL
            with lr_lib.etc.pool.main_pool.init() as (lr_vars.M_POOL, lr_vars.T_POOL):

                # core/gui
                with _start(excepthook=excepthook) as ex:
                    if any(ex):  # выход - в теле with работа уже окончена
                        lr_lib.etc.excepthook.full_tb_write(*ex)
    return


@contextlib.contextmanager
def _start(excepthook=True, console_args=sys.argv) -> iter(((None, None, None), )):
    """запуск core/gui"""
    if excepthook:  # перехват raise -> lr_vars.Logger.error
        lr_vars.Tk.report_callback_exception = lr_lib.etc.excepthook.excepthook
    try:

        as_console = bool(console_args[1:])
        c_args = lr_lib.core.main_core.init(as_console=as_console)

        if as_console:  # консольное использование
            lr_lib.core.main_core.start(c_args, echo=True)

        else:  # gui использование
            with lr_lib.etc.keyb.keyboard_listener():  # hotkey(param from clipboard)
                lr_lib.gui.main_gui.init(c_args)
                lr_lib.gui.main_gui.start(action=True, lock=True)

        yield sys.exc_info()
    except Exception as ex:
        lr_lib.etc.excepthook.excepthook(ex)
    else:
        lr_vars.Logger.trace('Exit\nas_console={c}\nconsole_args={cas}\nc_args={ca}'.format(
            c=as_console, cas=console_args, ca=c_args))
    finally:
        if excepthook:
            lr_vars.Tk.report_callback_exception = lr_vars.original_callback_exception
    return
