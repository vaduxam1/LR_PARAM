# -*- coding: UTF-8 -*-
# v9.2 __main__

import sys
import contextlib

from lr_lib import (
    defaults,
    var_setter as lr_setter,
    files as lr_files,
    param as lr_param,
    pool as lr_pool,
    other as lr_other,
    window as lr_window,
    logger as lr_log,
)


@contextlib.contextmanager
def lr_starter() -> iter((None, )):
    '''запуск скрипта'''
    defaults.Logger.info('version={v}, sys.getdefaultencoding={e}, defaults.VarEncode={ce}'.format(v=defaults.VERSION, e=sys.getdefaultencoding(), ce=defaults.VarEncode.get()))
    defaults.Tk.report_callback_exception = lr_other.excepthook  # !!! перехват raise!!!

    lr_setter.initVars()  # связь основных Var
    try:
        if sys.argv[1:]:  # консольное использование
            args_dict = lr_other.argument_parser()
            lr_files.createAllFiles()  # создать файлы
            defaults.VarParam.set(args_dict['param'])  # найти
            web_reg_save_param = lr_param.create_web_reg_save_param()  # сформировать
            yield defaults.Logger.info(web_reg_save_param, notepad=True)  # отобразить

        else:  # gui использование
            lr_other.keyboard_listener()  # hotkey
            defaults.Window = lr_window.Window(action=True, auto_param_creator=False)
            yield defaults.Tk.mainloop()  # заблокировать
    finally:
        defaults.Tk.report_callback_exception = sys.excepthook


if __name__ == '__main__':
    # вся работа в lr_starter(), в теле with - уже выход
    with lr_log.Logger_Creator(), lr_pool.MainThreadUpdater(), lr_pool.POOL_Creator(), lr_starter():
        defaults.Logger.info('выход, sys.exc_info: {}'.format(sys.exc_info()))
    sys.exit(0)
