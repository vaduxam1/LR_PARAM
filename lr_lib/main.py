# -*- coding: UTF-8 -*-
# старт классов скрипта
# пример главного запускающего файла lr_start.py:
# from lr_lib.main import start
# if __name__ == '__main__':
    # start()

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


@contextlib.contextmanager
def _start(console_args=sys.argv):
    '''запуск core/gui'''
    lr_core.init()  # проинициализировать

    # работа
    if console_args[1:]:  # консольное использование
        lr_core.console_start(echo=True)
    else:  # gui использование
        with lr_keyb.keyboard_listener():  # hotkey(param from clipboard)
            lr_gui.init(mainloop_lock=True, action=True, auto_param_creator=False)  # lock=True

    yield sys.exc_info()  # выход
    lr_vars.Logger.trace('Exit | console_args: {}'.format(console_args))


def start(with_callback_exception=True):
    '''инит дополнительных классов и запуск скрипта'''
    with lr_logger.init(name='__main__', encoding='cp1251', levels=lr_vars.loggingLevels) as Logger:
        lr_vars.Logger = Logger
        lr_vars.Logger.info('version={v}, defaults.VarEncode={ce}\n{si}'.format(
            v=lr_vars.VERSION, ce=lr_vars.VarEncode.get(), si=lr_sysinfo.system_info()))

        with lr_other_pool.MainThreadUpdater() as main_executer, lr_main_pool.POOL_Creator() as mt_pools:
            lr_vars.MainThreadUpdater = main_executer
            (lr_vars.M_POOL, lr_vars.T_POOL) = mt_pools

            lr_starter = (_start_with_callback_exception if with_callback_exception else _start)
            with lr_starter() as exc_info:  # core/gui инит
                if any(exc_info):  # вся работа в _start(), в теле with - работа уже окончена
                    return lr_excepthook.full_tb_write(*exc_info)


@contextlib.contextmanager
def _start_with_callback_exception() -> iter((None, )):
    '''запуск в обертке excepthook(перехват raise)'''
    lr_vars.Tk.report_callback_exception = lr_excepthook.excepthook
    try:
        with _start() as err:
            yield err
    finally:
        lr_vars.Tk.report_callback_exception = sys.excepthook
