# -*- coding: UTF-8 -*-
# старт скрипта

import sys
import contextlib

import lr_lib.gui.main as lr_gui
import lr_lib.core.main as lr_core
import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.logger as lr_logger
import lr_lib.core.etc.other as lr_other
import lr_lib.etc.pool.main_pool as lr_main_pool
import lr_lib.etc.pool.other as lr_other_pool


@contextlib.contextmanager
def _start():
    '''запуск core/gui'''
    lr_core.init()  # проинициализировать

    # работа
    if sys.argv[1:]:  # консольное использование
        lr_core.console_start(echo=True)
    else:  # gui использование
        lr_other.keyboard_listener()  # hotkey(param from clipboard)
        lr_gui.init(mainloop_lock=True, action=True, auto_param_creator=False)

    yield sys.exc_info()  # выход


def start() -> bool:
    '''запуск скрипта'''
    with lr_logger.init(name='__main__', encoding='cp1251', levels=lr_vars.loggingLevels) as Logger:
        lr_vars.Logger = Logger

        lr_vars.Logger.trace(sys.exc_info())
        lr_vars.Logger.info('version={v}, sys.getdefaultencoding={e}, defaults.VarEncode={ce}'.format(
            v=lr_vars.VERSION, e=sys.getdefaultencoding(), ce=lr_vars.VarEncode.get()))

        with lr_other_pool.MainThreadUpdater() as main_executer, lr_main_pool.POOL_Creator() as mt_pools:
            lr_vars.MainThreadUpdater = main_executer
            (lr_vars.M_POOL, lr_vars.T_POOL) = mt_pools

            with run_with_report_callback_exception() as err:  # core/gui инит
                # вся работа в _start(), в теле with - работа окончена
                exc_info = exc_type, exc_val, exc_tb = err
                if any(exc_info):
                    lr_other.full_tb_write(exc_type, exc_val, exc_tb)
                    return exc_info


@contextlib.contextmanager
def run_with_report_callback_exception() -> iter((None, )):
    '''запуск скрипта в excepthook(перехват raise) обертке'''
    lr_vars.Tk.report_callback_exception = lr_other.excepthook
    try:
        with _start() as err:
            yield err
    finally:
        lr_vars.Tk.report_callback_exception = sys.excepthook


if __name__ == '__main__':
    # import sys
    # from lr_lib.main import start
    s = start()
    sys.exit(s)  # any(s) == error
