# -*- coding: UTF-8 -*-
# tk.Text виджет

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.gui.wrsp.win_block
import lr_lib.core.var.vars as lr_vars


class WinText(lr_lib.gui.wrsp.win_block.WinBlock):
    """tk.Text"""
    def __init__(self):
        lr_lib.gui.wrsp.win_block.WinBlock.__init__(self)

        self.tk_text = tk.Text(
            self, foreground='grey', background=lr_vars.Background, wrap=tk.NONE, height=10, padx=0, pady=0, undo=True,
        )

        self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
        self.tk_text.configure(
            yscrollcommand=self.text_scrolly.set, xscrollcommand=self.text_scrollx.set, bd=0, padx=0, pady=0)
        return

    def add_message(self, levelname: str, text: str) -> None:
        """сообщения в конец текста gui"""
        if lr_vars.loggingLevels[lr_vars.VarWindowLogger.get()] <= lr_vars.loggingLevels[levelname]:
            self.tk_text.insert(tk.END, '{}\n'.format(text))
            self.tk_text.see(tk.END)
        return

    def print(self, levelname: str, text: str) -> None:
        """сообщения в конец текста gui, в main потоке"""
        lr_vars.MainThreadUpdater.submit(lambda: self.add_message(levelname, text))
        return
