# -*- coding: UTF-8 -*-
# все варианты создания web_reg_save_param
import threading
import time

import lr_lib
from lr_lib.core.var import vars as lr_vars


class ColorProgress:
    """
    менять цвет action.c окна при "работе" поиска всех вариантов создания web_reg_save_param
    """
    def __init__(self, action: 'lr_lib.gui.action.main_action.ActionWindow',
                 **color_set_kwargs):
        self.is_work = [True]
        self.action = action
        self.color_set_kwargs = color_set_kwargs
        return

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            lr_lib.etc.excepthook.excepthook(exc_type, exc_val, exc_tb)
        self.stop()
        return exc_type, exc_val, exc_tb

    def stop(self) -> None:
        """остановка"""
        self.is_work.clear()
        return

    def start(self) -> None:
        """циклическая смена цвета"""
        t = threading.Thread(target=self._start)
        t.start()
        return

    def _start(self) -> None:
        """циклическая смена цвета"""
        while self.is_work:
            self.color_change(None)  # смена цвета
            time.sleep(lr_vars._MTUT)
            continue

        self.color_change('')  # оригинальный цвет
        return

    def color_change(self, color: 'None or ""') -> None:
        """смена цвета"""
        callback = lambda: self.action.background_color_set(color=color, **self.color_set_kwargs)
        lr_vars.MainThreadUpdater.submit(callback)  # action цвет
        return


def progress_decor(func, action=None):
    """декоратор - навесить цветной прогрессбар на команды меню мыши"""
    def wrap(*args, **kwargs):
        act = (args[0] if (action is None) else action)
        with lr_lib.gui.etc.color_progress.ColorProgress(act):
            _ = func(*args, **kwargs)
        return
    return wrap