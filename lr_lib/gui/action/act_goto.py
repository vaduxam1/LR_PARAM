# -*- coding: UTF-8 -*-
# action.с окно - виджеты перехода по тексту

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.action.act_font


class ActGoto(lr_lib.gui.action.act_font.ActFont):
    """виджеты перехода по тексту"""

    def __init__(self):
        lr_lib.gui.action.act_font.ActFont.__init__(self)

        self.inf_combo = ttk.Combobox(self.inf_bar, justify='center', font=lr_vars.DefaultFont)
        self.inf_combo.bind("<KeyRelease-Return>", self.goto_inf)
        self.inf_combo.bind("<<ComboboxSelected>>", self.goto_inf)

        self.wrsp_combo = ttk.Combobox(self.wrsp_bar, justify='center', font=lr_vars.DefaultFont)
        self.wrsp_combo.bind("<KeyRelease-Return>", self.goto_wrsp)
        self.wrsp_combo.bind("<<ComboboxSelected>>", self.goto_wrsp)

        self.param_combo = ttk.Combobox(self.wrsp_bar, justify='center', font=lr_vars.DefaultFont)
        self.param_combo.bind("<KeyRelease-Return>", self.goto_param)
        self.param_combo.bind("<<ComboboxSelected>>", self.goto_param)

        self.transaction_combo = ttk.Combobox(self.transaction_bar, justify='center', font=lr_vars.DefaultFont)
        self.transaction_combo.bind("<KeyRelease-Return>", self.goto_transaction)
        self.transaction_combo.bind("<<ComboboxSelected>>", self.goto_transaction)
        return

    def goto_inf(self, *args) -> None:
        try:
            self.search_in_action(word=lr_lib.core.wrsp.param.Snap.format(num=self.inf_combo.get().strip()), hist=False)
        except tk.TclError as ex:
            pass
        return

    def goto_transaction(self, *args) -> None:
        try:
            self.search_in_action(word=self.transaction_combo.get(), hist=False)
        except tk.TclError as ex:
            pass
        return

    def goto_param(self, *args) -> None:
        try:
            self.search_in_action(word=self.param_combo.get(), hist=False)
        except tk.TclError as ex:
            pass
        return

    def goto_wrsp(self, *args) -> None:
        try:
            self.search_in_action(word=self.wrsp_combo.get(), hist=False)
        except tk.TclError as ex:
            pass
        return

    def inf_combo_set(self) -> None:
        self.inf_combo['values'] = list(self.web_action.action_infs)
        if self.inf_combo['values']:
            self.inf_combo.current(0)
        return

    def wrsp_combo_set(self) -> None:
        self.wrsp_combo['values'] = list(self.web_action.websReport.wrsp_and_param_names.keys())
        return

    def param_combo_set(self) -> None:
        try:
            self.param_combo['values'] = list(self.web_action.websReport.wrsp_and_param_names.values())
        except Exception as ex:
            pass
        return

    def transaction_combo_set(self) -> None:
        self.transaction_combo['values'] = self.transaction
        return
