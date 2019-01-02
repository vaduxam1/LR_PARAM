# -*- coding: UTF-8 -*-
# выбор каталога файлов ответов

import tkinter as tk

from tkinter import filedialog

import lr_lib
import lr_lib.gui.wrsp.win_other
import lr_lib.core.var.vars as lr_vars


class WinFolder(lr_lib.gui.wrsp.win_other.WinOther):
    """выбор каталога файлов ответов"""
    def __init__(self):
        lr_lib.gui.wrsp.win_other.WinOther.__init__(self)

        self.Button_change_folder = tk.Button(
            self.last_frame, text='folder', padx=0, pady=0, command=self.change_folder_ask,
            font=lr_vars.DefaultFont + ' italic bold')

        self.change_folder_cbx = tk.Checkbutton(
            self.last_frame, variable=lr_vars.VarIsSnapshotFiles, padx=0, pady=0, font=lr_vars.DefaultFont + ' italic',
            command=self.set_folder, text='lr')

        self.deny_file_cbx = tk.Checkbutton(
            self.last_frame, variable=lr_vars.VarAllowDenyFiles, padx=0, pady=0, font=lr_vars.DefaultFont + ' italic',
            command=self.set_folder, text='deny')

        self.filesStats_cbx = tk.Checkbutton(
            self.last_frame, variable=lr_vars.VarAllFilesStatistic, padx=0, pady=0, text='stat',
            font=lr_vars.DefaultFont + ' italic', command=self.set_folder)
        return

    def set_folder(self) -> None:
        """установка folder"""
        self.clear()
        with self.block():
            lr_lib.core.wrsp.files.init()

        self.last_frame_text_set()
        self.setSortKey1()
        return

    def change_folder_ask(self, *args) -> None:
        """смена директории поиска файлов"""
        d = filedialog.askdirectory()
        if d:
            lr_vars.VarFilesFolder.set(d)
            with self.block():
                lr_lib.core.wrsp.files.init()
            self.clear()
        return
