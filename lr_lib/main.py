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
    '''инит дополнительных классов и запуск скрипта'''
    with lr_logger.init(name='__main__', encoding='cp1251', levels=lr_vars.loggingLevels) as Logger:
        lr_vars.Logger = Logger
        lr_vars.Logger.info('version={v}, defaults.VarEncode={ce}\n{si}'.format(
            v=lr_vars.VERSION, ce=lr_vars.VarEncode.get(), si=lr_sysinfo.system_info()))

        with lr_other_pool.MainThreadUpdater() as mtu, lr_main_pool.POOL_Creator() as mp_tp:
            lr_vars.MainThreadUpdater = mtu
            (lr_vars.M_POOL, lr_vars.T_POOL) = mp_tp

            # вся работа в _start(), в теле with - работа уже окончена
            with (_excepthook() if excepthook else _start()) as ex:  # core/gui инит
                if any(ex):
                    lr_excepthook.full_tb_write(*ex)


@contextlib.contextmanager
def _start(console_args=sys.argv):
    '''запуск core/gui'''
    as_console = bool(console_args[1:])  # консольное использование
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


@contextlib.contextmanager
def _excepthook() -> iter((None, )):
    '''запуск в обертке excepthook(перехват raise)'''
    lr_vars.Tk.report_callback_exception = lr_excepthook.excepthook
    try:
        with _start() as e:
            yield e
    finally:
        lr_vars.Tk.report_callback_exception = sys.excepthook
