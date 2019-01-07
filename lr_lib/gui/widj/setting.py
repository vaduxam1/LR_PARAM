# -*- coding: UTF-8 -*-
# окно настройки

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_other
import lr_lib.core_gui.rename


class WrspSettingWindow(tk.Toplevel):
    """настройка var"""
    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow'):
        super().__init__(padx=0, pady=0)
        self.parent = parent
        self.transient(self.parent)
        self.resizable(width=False, height=False)
        self.title('настройка')


        lr_lib.gui.etc.gui_other.center_widget(self)
        return
