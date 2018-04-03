# -*- coding: UTF-8 -*-
# Toplevel окно кодировки

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars


class TopEncoding(tk.Toplevel):
    """окно кодировки файлов"""
    def __init__(self, action: 'lr_lib.gui.wrsp.main_window.Window'):
        tk.Toplevel.__init__(self)
        self.action = action

        self.transient(action)
        self.resizable(width=False, height=False)
        tt = 'кодировка файлов для (2)-(5)\n\t# Window.enc_wind'
        self.title(tt)

        encodeEntry = ttk.Combobox(
            self, justify='center', textvariable=lr_vars.VarEncode, width=65, foreground='grey',
            background=lr_vars.Background, font=lr_vars.DefaultFont + ' italic')

        encodeEntry['values'] = lr_vars.ENCODE_LIST
        encodeEntry.bind("<<ComboboxSelected>>", lambda *a: self.action.comboFiles_change())

        lr_lib.gui.widj.tooltip.createToolTip(encodeEntry, tt)
        encodeEntry.pack()
        lr_lib.gui.etc.gui_other.center_widget(self)

