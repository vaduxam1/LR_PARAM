# -*- coding: UTF-8 -*-
# осортировка файлов, файловыми ключами

import itertools
import tkinter.ttk as ttk

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.wrsp.win_maxmin


def deny_keys(key: str) -> bool:
    """
    не t123 keys
    """
    tk = (key[0] == 't')
    ak = all(map(str.isnumeric, key[1:]))
    b = (not (tk and ak))
    return b


class WinFileSort(lr_lib.gui.wrsp.win_maxmin.WinMaxMin):
    """
    сортировка файлов, файловыми ключами
    """

    def __init__(self):
        lr_lib.gui.wrsp.win_maxmin.WinMaxMin.__init__(self)

        self.sortKey1 = ttk.Combobox(
            self.last_frame, textvariable=lr_vars.VarFileSortKey1, justify='center', width=10,
            font=(lr_vars.DefaultFont + ' italic'), style="BW.TButton",
        )

        self.sortKey2 = ttk.Combobox(
            self.last_frame, textvariable=lr_vars.VarFileSortKey2, justify='center',
            font=(lr_vars.DefaultFont + ' italic'), style="BW.TButton",
        )

        self.sortKey1.bind("<<ComboboxSelected>>", self.setSortKey1)
        self.sortKey2.bind("<<ComboboxSelected>>", self.setSortKey2)
        return

    def setSortKeys(self) -> None:
        """
        задать комбо(1/2) сортировки
        """
        keys = set(itertools.chain(*lr_vars.AllFiles))
        keys = filter(deny_keys, keys)
        self.sortKey1['values'] = list(keys)

        k1 = lr_vars.VarFileSortKey1.get()
        self.sortKey1.set(k1)
        self.setSortKey1()

        k2 = lr_vars.VarFileSortKey2.get()
        self.sortKey2.set(k2)
        return

    def setSortKey1(self, *args, _none=()) -> None:
        """
        комбо сортировки 1
        """
        k1 = self.sortKey1.get()
        lr_vars.VarFileSortKey1.set(k1)
        ic = itertools.chain(lr_vars.AllFiles, lr_vars.FilesWithParam)
        s = set(k for f in ic for k in f.get(k1, _none))

        self.sortKey2['values'] = list(s)
        self.sortKey2.set('')
        return

    def setSortKey2(self, *args) -> None:
        """
        комбо сортировки файлов
        """
        k2 = self.sortKey2.get()
        lr_vars.VarFileSortKey2.set(k2)
        if lr_vars.FilesWithParam:
            self.get_files()  # сортировка при поиске
        return
