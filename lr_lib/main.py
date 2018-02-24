# -*- coding: UTF-8 -*-
# старт классов скрипта
# пример главного запускающего файла lr_start.py:
# from lr_lib.main import init
# if __name__ == '__main__':
    # init()

import sys
import contextlib

import lr_lib.gui.main_gui as lr_gui
import lr_lib.core.main_core as lr_core
import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.logger as lr_logger
import lr_lib.etc.sysinfo as lr_sysinfo
import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.etc.keyb as lr_keyb
import lr_lib.etc.pool.main_pool as lr_main_pool
import lr_lib.etc.pool.other as lr_other_pool


def init(excepthook=True):
    """инит дополнительных классов, сохр. их в lr_vars, запуск core/gui"""
    # lr_vars.Logger
    with lr_logger.init(name='__main__', encoding='cp1251', levels=lr_vars.loggingLevels) as lr_vars.Logger:
        lr_vars.Logger.info('version={v}, defaults.VarEncode={ce}\n{si}'.format(
            v=lr_vars.VERSION, ce=lr_vars.VarEncode.get(), si=lr_sysinfo.system_info()))

        # lr_vars.MainThreadUpdater
        with lr_other_pool.MainThreadUpdater().init() as lr_vars.MainThreadUpdater:

            # lr_vars.M_POOL, lr_vars.T_POOL
            with lr_main_pool.init() as (lr_vars.M_POOL, lr_vars.T_POOL):

                # работа скрипта - внутри _start(core/gui)
                with (_with_except(_start)() if excepthook else _start()) as ex:

                    if any(ex):  # выход - в теле with работа уже окончена
                        lr_excepthook.full_tb_write(*ex)


@contextlib.contextmanager
def _start(console_args=sys.argv) -> iter(((None, None, None), )):
    """запуск core/gui"""
    as_console = bool(console_args[1:])
    c_args = lr_core.init(as_console=as_console)

    if as_console:  # консольное использование
        lr_core.start(c_args, echo=True)

    else:  # gui использование
        with lr_keyb.keyboard_listener():  # hotkey(param from clipboard)
            lr_gui.init(action=True)
            lr_gui.start()  # lock

    yield sys.exc_info()
    lr_vars.Logger.trace('Exit\nas_console={c}\nconsole_args={cas}\nc_args={ca}'.format(
        c=as_console, cas=console_args, ca=c_args))


def _with_except(func_start: callable) -> callable:
    """декоратор запуска в обертке excepthook(перехват raise -> lr_vars.Logger.error)
    """
    @contextlib.contextmanager
    def start(*args, **kwargs):
        lr_vars.Tk.report_callback_exception = lr_excepthook.excepthook
        try:
            with func_start(*args, **kwargs) as exc_info:
                yield exc_info
        finally:
            lr_vars.Tk.report_callback_exception = sys.excepthook

    return start
