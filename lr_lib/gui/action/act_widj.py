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

