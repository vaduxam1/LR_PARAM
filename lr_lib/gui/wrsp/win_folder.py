# -*- coding: UTF-8 -*-
# выбор каталога файлов ответов

import tkinter as tk

from tkinter import filedialog

import lr_lib.gui.wrsp.win_other as lr_win_other
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.files as lr_files


class WinFolder(lr_win_other.WinOther):
    """выбор каталога файлов ответов"""
    def __init__(self):
        lr_win_other.WinOther.__init__(self)

        self.Button_change_folder = tk.Button(
            self.last_frame, text='folder', padx=0, pady=0, command=self.change_folder_ask,
            font=lr_vars.DefaultFont + ' italic bold')

        self.change_folder_cbx = tk.Checkbutton(
            self.last_frame, variable=lr_vars.VarIsSnapshotFiles, padx=0, pady=0, font=lr_vars.DefaultFont + ' italic',
            command=self.set_folder, text='')

        self.deny_file_cbx = tk.Checkbutton(
            self.last_frame, variable=lr_vars.VarAllowDenyFiles, padx=0, pady=0, font=lr_vars.DefaultFont + ' italic',
            command=self.set_folder, text='')

        self.filesStats_cbx = tk.Checkbutton(
            self.last_frame, variable=lr_vars.VarAllFilesStatistic, padx=0, pady=0, text='',
            font=lr_vars.DefaultFont + ' italic', command=self.set_folder)

    def set_folder(self) -> None:
        """установка folder"""
        self.clear()
        with self.block():
            lr_files.init()

        self.last_frame_text_set()
        self.setSortKey1()

    def change_folder_ask(self, *args) -> None:
        """смена директории поиска файлов"""
        d = filedialog.askdirectory()
        if d:
            lr_vars.VarFilesFolder.set(d)
            with self.block():
                lr_files.init()
            self.clear()

