# -*- coding: UTF-8 -*-
# ttk.Frame Win-окна

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight


class WinFrame(tk.Frame):
    """
    ttk.Frame
        main_window.Window
        win_menu.WinMenu
        win_folder.WinFolder
        win_other.WinOther
        win_filesort.WinFileSort
        win_maxmin.WinMaxMin
        win_widj.WinWidj
        win_part_lbrb.WinPartsLbRb
        win_text.WinText
        win_block.WinBlock
        win_act.WinAct
      + win_frame.WinFrame
      + ttk.Frame
    """

    def __init__(self):
        lr_vars.Tk.protocol("WM_DELETE_WINDOW", self.on_closing)
        lr_vars.Tk.geometry('{}x{}'.format(*lr_vars._Tk_WIND_SIZE))
        lr_vars.Tk.option_add("*Listbox*Background", lr_lib.core.var.vars_highlight.Background)
        lr_vars.Tk.option_add("*Frame*Background", lr_lib.core.var.vars_highlight.Background)
        lr_vars.Tk.option_add("*Toplevel*Background", lr_lib.core.var.vars_highlight.Background)

        tk.Frame.__init__(self, lr_vars.Tk)
        self.config(background=lr_lib.core.var.vars_highlight.Background)

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
            self, bd=2, labelanchor=tk.N, relief='groove', padx=0, pady=0, font=lr_vars.DefaultFont,
        )
        self.mid_frame = tk.Frame(self.main_frame, )
        self.find_frame = tk.Frame(self.main_frame, )
        self.show_param_frame = tk.Frame(self.main_frame, )
        self.last_frame = tk.LabelFrame(
            self, labelanchor=tk.S, bd=1, relief='groove', padx=0, pady=0, font=lr_vars.DefaultFont,
        )
        return

    def on_closing(self) -> None:
        """
        не выходить, при открытых action.c окнах
        """
        tt = "Есть открытые action.c окна\n{a}\nвсе равно выйти?".format(a=', '.join(map(str, self.action_windows)))
        if (not self.action_windows) or tk.messagebox.askokcancel('выход', tt):
            self.destroy()
            lr_vars.Tk.destroy()
        return

    def clip_add(self, text: str) -> None:
        """
        буфер обмена
        """
        self.clipboard_clear()
        self.clipboard_append(text)
        return
