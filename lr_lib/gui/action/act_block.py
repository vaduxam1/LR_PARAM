# -*- coding: UTF-8 -*-
# action.с окно - блокирование виджетов

import contextlib

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.action.act_scroll as lr_act_scroll


class ActBlock(lr_act_scroll.ActScrollText):
    """блокировка виджетов"""

    def __init__(self):
        lr_act_scroll.ActScrollText.__init__(self)

        self.unblock = tk.Button(
            self.file_bar, text='unblock', font=lr_vars.DefaultFont + ' bold', command=lambda *a: self._block(False))

    @contextlib.contextmanager
    def block(self, w=('tk_text', 'unblock', 'search_entry', 'search_res_combo', 'toolbar',),
              no_highlight=False) -> iter:
        """заблокировать/разблокировать виджеты в gui"""
        highlight = self.tk_text.highlight_var.get()

        if no_highlight:  # откл подсветку
            self.tk_text.highlight_var.set(False)
        try:
            yield self._block(True, w=w)
        finally:
            self._block(False, w=w)
            if no_highlight:  # вкл подсветку
                self.tk_text.highlight_var.set(highlight)
                self.tk_text.action.tk_text.highlight_apply()

    def _block(self, bl: bool, w=()) -> None:
        """заблокировать/разблокировать виджеты в gui"""

        def set_block(state=('disabled' if bl else 'normal')):
            """заблокировать/разблокировать"""
            for attr in dir(self):
                if not attr.startswith('_') and (attr not in w):
                    with contextlib.suppress(AttributeError, tk.TclError):
                        getattr(self, attr).configure(state=state)
            self.update()

        lr_vars.MainThreadUpdater.submit(set_block)

