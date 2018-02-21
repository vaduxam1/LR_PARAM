# -*- coding: UTF-8 -*-
# ttk.Frame Win-окна

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.core.var.vars as lr_vars


class WinFrame(ttk.Frame):
    """ttk.Frame"""
    def __init__(self):
        ttk.Frame.__init__(self, lr_vars.Tk, padding="0 0 0 0")

        lr_vars.Tk.protocol("WM_DELETE_WINDOW", self.on_closing)
        lr_vars.Tk.geometry('{}x{}'.format(*lr_vars._Tk_WIND_SIZE))
        lr_vars.Tk.option_add("*Listbox*Background", lr_vars.Background)

        # "масштабирование" виджетов окна
        lr_vars.Tk.grid_rowconfigure(0, weight=1)
        lr_vars.Tk.grid_columnconfigure(0, weight=1)
        lr_vars.Tk.title(lr_vars.VERSION)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=tk.NSEW)

        # vars
        self.action_windows = {}  # WinAct пересоздаст
        self.no_param_text = ''
        self.no_files_text = ''
        self.param_hist_list = ['']

        # frame
        self.main_frame = tk.LabelFrame(
            self, bd=2, labelanchor=tk.N, relief='groove', padx=0, pady=0, font=lr_vars.DefaultFont)
        self.mid_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.find_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.show_param_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.last_frame = tk.LabelFrame(
            self, labelanchor=tk.S, bd=1, relief='groove', padx=0, pady=0, font=lr_vars.DefaultFont)

    def on_closing(self) -> None:
        """не выходить, при открытых action.c окнах"""
        if (not self.action_windows) or tk.messagebox.askokcancel(
                'выход', "Есть открытые action.c окна\n{a}\nвсе равно выйти?".format(
                    a=', '.join(map(str, self.action_windows)))):
            self.destroy()
            lr_vars.Tk.destroy()

    def clip_add(self, text: str) -> None:
        """буфер обмена"""
        self.clipboard_clear()
        self.clipboard_append(text)
