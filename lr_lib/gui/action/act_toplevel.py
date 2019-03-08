# -*- coding: UTF-8 -*-
# action.с окно - Toplevel

import tkinter as tk
from tkinter import messagebox

import lr_lib.core.var.vars as lr_vars


class ActToplevel(tk.Toplevel):
    """
    окно Toplevel
        main_action.ActionWindow
        act_win.ActWin
        act_any.ActAny
        act_goto.ActGoto
        act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
        act_serializ.TkTextWebSerialization
        act_backup.ActBackup
        act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
        act_var.ActVar
      + act_toplevel.ActToplevel
      + tk.Toplevel
    """

    def __init__(self):
        tk.Toplevel.__init__(self, padx=0, pady=0)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.geometry('{}x{}'.format(*lr_vars._Tk_ActionWIND_SIZE))
        return

    def on_closing(self) -> None:
        """
        спросить, при закрытии окна
        """
        if messagebox.askokcancel("Закрыть action.c", "Закрыть action.c ?", parent=self):
            self.destroy()
        return
