# -*- coding: UTF-8 -*-
# виджеты min_inf / max_inf

import tkinter.ttk as ttk

import lr_lib
import lr_lib.gui.wrsp.win_widj
import lr_lib.core.var.vars as lr_vars


class WinMaxMin(lr_lib.gui.wrsp.win_widj.WinWidj):
    """min_inf / max_inf"""
    def __init__(self):
        lr_lib.gui.wrsp.win_widj.WinWidj.__init__(self)

        self.max_inf = ttk.Combobox(
            self.show_param_frame, width=10, textvariable=lr_vars.VarSearchMaxSnapshot, justify='center',
            foreground='grey', font=lr_vars.DefaultFont, style="BW.TButton")

        self.min_inf = ttk.Combobox(
            self.show_param_frame, width=10, textvariable=lr_vars.VarSearchMinSnapshot, justify='center',
            foreground='grey', font=lr_vars.DefaultFont, style="BW.TButton")

        self.max_inf.bind("<<ComboboxSelected>>", self._min_max_set)
        self.min_inf.bind("<<ComboboxSelected>>", self._min_max_set)
        return

    def _min_max_set(self, *args) -> None:
        """max/min_inf"""
        if lr_vars.FilesWithParam:
            self.get_files()
        return

    def set_maxmin_inf(self, files):
        """установка виджетов min_inf max_inf"""
        infs = list(lr_lib.core.etc.other.get_files_infs(files))
        self.max_inf['values'] = list(reversed(infs))
        self.min_inf['values'] = infs

        self.max_inf.set(max(infs or [-1]))
        self.min_inf.set(min(infs or [-1]))
        return
