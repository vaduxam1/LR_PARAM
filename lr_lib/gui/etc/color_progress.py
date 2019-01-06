# -*- coding: UTF-8 -*-
# все варианты создания web_reg_save_param
import threading
import time

import lr_lib
import lr_lib.gui.etc.color_change
from lr_lib.core.var import vars as lr_vars
import lr_lib.core.var.vars_highlight


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
            # ждать
            time.sleep(lr_lib.core.var.vars_highlight.ColorProgressDelay)
            continue

        self.color_change('')  # оригинальный цвет
        return

    def color_change(self, color: 'None or ""') -> None:
        """смена цвета"""
        callback = lambda: lr_lib.gui.etc.color_change.background_color_set(
            self.action, color=color, **self.color_set_kwargs)
        lr_vars.MainThreadUpdater.submit(callback)  # action цвет
        return


def progress_decor(func, action=None):
    """декоратор - навесить цветной прогрессбар"""
    def wrap(*args, **kwargs):
        p = ColorProgress(args[0] if (action is None) else action)
        p.__enter__()
        try:
            return func(*args, **kwargs)
        finally:
            p.__exit__(None, None, None, )
    return wrap
