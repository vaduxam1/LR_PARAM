# -*- coding: UTF-8 -*-
# action.с окно - блокирование виджетов

import contextlib

import tkinter as tk

import lr_lib.gui.action.act_scroll
import lr_lib.core.var.vars as lr_vars


class ActBlock(lr_lib.gui.action.act_scroll.ActScrollText):
    """блокировка виджетов"""

    def __init__(self):
        lr_lib.gui.action.act_scroll.ActScrollText.__init__(self)

        self.unblock = tk.Button(
            self.file_bar, text='unblock', font=lr_vars.DefaultFont + ' bold', command=lambda *a: self._block(False))
        return

    @contextlib.contextmanager
    def block(self, w=('tk_text', 'unblock', 'search_entry', 'search_res_combo', 'toolbar',)) -> iter:
        """заблокировать/разблокировать виджеты в gui"""
        try:
            lr_vars.MainThreadUpdater.submit(lambda: self._block(True, w=w))
            yield
        finally:
            lr_vars.MainThreadUpdater.submit(lambda: self._block(False, w=w))
        return

    def _block(self, bl: bool, w=()) -> None:
        """заблокировать/разблокировать виджеты в gui"""
        state = ('disabled' if bl else 'normal')

        for attr in dir(self):
            if (not attr.startswith('_')) and (attr not in w):
                with contextlib.suppress(AttributeError, tk.TclError):
                    getattr(self, attr).configure(state=state)
            continue

        self.update()
        return
