# -*- coding: UTF-8 -*-
# осортировка файлов, файловыми ключами

import itertools

import tkinter.ttk as ttk

import lr_lib.gui.wrsp.win_maxmin
import lr_lib.core.var.vars as lr_vars


class WinFileSort(lr_lib.gui.wrsp.win_maxmin.WinMaxMin):
    """сортировка файлов, файловыми ключами"""
    def __init__(self):
        lr_lib.gui.wrsp.win_maxmin.WinMaxMin.__init__(self)

        self.sortKey1 = ttk.Combobox(
            self.last_frame, textvariable=lr_vars.VarFileSortKey1, justify='center', width=10,
            font=lr_vars.DefaultFont + ' italic', style="BW.TButton")

        self.sortKey2 = ttk.Combobox(
            self.last_frame, textvariable=lr_vars.VarFileSortKey2, justify='center',
            font=lr_vars.DefaultFont + ' italic', style="BW.TButton")

        self.sortKey1.bind("<<ComboboxSelected>>", self.setSortKey1)
        self.sortKey2.bind("<<ComboboxSelected>>", self.setSortKey2)
        return

    def setSortKeys(self) -> None:
        """задать комбо(1/2) сортировки"""
        k1 = set(k for f in lr_vars.AllFiles for k in f)
        self.sortKey1['values'] = sorted(k for k in k1 if (not ((k[0] == 't') and all(map(str.isnumeric, k[1:])))))
        self.sortKey1.set(lr_vars.VarFileSortKey1.get())
        self.setSortKey1()

        self.sortKey2.set(lr_vars.VarFileSortKey2.get())
        return

    def setSortKey1(self, *args) -> None:
        """комбо сортировки 1"""
        lr_vars.VarFileSortKey1.set(self.sortKey1.get())
        s = set(k for f in itertools.chain(lr_vars.AllFiles, lr_vars.FilesWithParam)
                for k in f.get(self.sortKey1.get(), ()))

        self.sortKey2['values'] = list(s)
        self.sortKey2.set('')
        return

    def setSortKey2(self, *args) -> None:
        """комбо сортировки файлов"""
        lr_vars.VarFileSortKey2.set(self.sortKey2.get())
        if lr_vars.FilesWithParam:
            self.get_files()  # сортировка при поиске
        return
