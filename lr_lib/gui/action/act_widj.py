# -*- coding: UTF-8 -*-
# action.с окно - виджеты, которые надо создать первыми

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.gui.action.act_var as lr_act_var
import lr_lib.core.var.vars as lr_vars


class ActWidj(lr_act_var.ActVar):
    """виджеты, которые надо создать первыми"""

    def __init__(self):
        lr_act_var.ActVar.__init__(self)

        # bars
        self.toolbar = tk.LabelFrame(
            self, relief='ridge', bd=5, labelanchor=tk.N, font=lr_vars.DefaultFont + ' italic',
            text='для корректной работы, раскладку клавиатуры установить в ENG')

        self.middle_bar = tk.LabelFrame(self, relief='ridge', bd=2, text='', labelanchor=tk.S, font=lr_vars.DefaultFont)

        self.transaction_bar = tk.LabelFrame(
            self.middle_bar, relief='groove', bd=0, text='transaction', labelanchor=tk.S, font=lr_vars.DefaultFont)

        self.inf_bar = tk.LabelFrame(
            self.middle_bar, relief='groove', bd=0, text='inf', labelanchor=tk.S, font=lr_vars.DefaultFont)

        self.wrsp_bar = tk.LabelFrame(
            self.middle_bar, relief='groove', bd=0, text='web_reg_save_param', labelanchor=tk.S,
            font=lr_vars.DefaultFont)

        self.font_toolbar = tk.LabelFrame(
            self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.S, font=lr_vars.DefaultFont)

        self.file_bar = tk.LabelFrame(self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.N)
        self.cbx_bar = tk.LabelFrame(self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.S)

        #
        self.scroll_lab = tk.Label(self, text='0')
        self.scroll_lab2 = ttk.Label(self, text='0 %', background=lr_vars.Background)

        self.help1 = tk.Label(self, text='?', foreground='grey')
        self.help2 = tk.Label(self, text='?', foreground='grey')
        self.help3 = tk.Label(self, text='?', foreground='grey')

        self.var_bar_1 = tk.BooleanVar(value=lr_vars.var_bar_1)
        self.var_bar_2 = tk.BooleanVar(value=lr_vars.var_bar_2)
        self.var_bar_3 = tk.BooleanVar(value=lr_vars.var_bar_3)

    def show_hide_bar_1(self, force_show=False) -> None:
        """show/hide self.toolbar"""
        vb = self.var_bar_1.get()
        if force_show:
            if not vb:
                self.var_bar_1.set(True)
            else:
                return
        else:
            self.var_bar_1.set(not vb)

        if self.var_bar_1.get():
            self.toolbar.grid(row=2, column=0, sticky=tk.N, columnspan=100)
            self.help2.grid(row=2, column=201, sticky=tk.NSEW)
        else:
            self.toolbar.grid_remove()
            self.help2.grid_remove()

    def show_hide_bar_2(self) -> None:
        """show/hide self.middle_bar"""
        self.var_bar_2.set(not self.var_bar_2.get())
        if self.var_bar_2.get():
            self.middle_bar.grid(row=3, column=0, sticky=tk.N)
            self.help3.grid(row=3, column=201, sticky=tk.NSEW)
        else:
            self.middle_bar.grid_remove()
            self.help3.grid_remove()

    def show_hide_bar_3(self) -> None:
        """show/hide self.scroll_lab2"""
        self.var_bar_3.set(not self.var_bar_3.get())
        if self.var_bar_3.get():
            self.scroll_lab2.grid(row=2, column=300, sticky=tk.NSEW, rowspan=2)
            self.help2.grid(row=2, column=201, sticky=tk.NSEW)
            self.help3.grid(row=3, column=201, sticky=tk.NSEW)
        else:
            self.scroll_lab2.grid_remove()
            self.help2.grid_remove()
            self.help3.grid_remove()
