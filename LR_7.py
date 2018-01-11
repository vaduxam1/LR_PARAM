# -*- coding: UTF-8 -*-
# v9.0 __main__

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
def start() -> None:
    '''запуск'''
    try:
        lr_log.Logger_listener.start()  # старт логирования
        lr_log.Logger.info('version: {v} | sys.getdefaultencoding: {e} | defaults.VarEncode: {ce}'.format(
            v=defaults.VERSION, e=sys.getdefaultencoding(), ce=defaults.VarEncode.get()))
        defaults.Tk.report_callback_exception = lr_log.excepthook  # !!! перехват raise to logging !!!

        lr_pool.start()
        lr_setter.initVars()  # связь основных Var

        if sys.argv[1:]:  # консольное использование
            args_dict = lr_other.argument_parser()
            lr_files.createAllFiles()  # создать файлы

            defaults.VarParam.set(args_dict['param'])  # найти
            web_reg_save_param = lr_param.create_web_reg_save_param()  # сформировать
            lr_log.Logger.info(web_reg_save_param, notepad=True)  # отобразить
            yield False

        else:  # gui использование
            defaults.Window = lr_window.Window(action=True, auto_param_creator=False)
            lr_other.keyboard_listener()  # hotkey
            yield True

    finally:
        lr_pool.close()
        lr_log.Logger_listener.stop()  # стоп логирования
        defaults.Tk.report_callback_exception = sys.excepthook


if __name__ == '__main__':
    with start() as is_gui:
        if is_gui:  # lock
            defaults.Tk.mainloop()
    sys.exit(sys.exc_info())
