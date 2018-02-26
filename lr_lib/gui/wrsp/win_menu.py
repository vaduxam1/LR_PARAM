# -*- coding: UTF-8 -*-
# меню gui окна

import contextlib

import tkinter as tk

from tkinter import filedialog

import lr_lib.gui.wrsp.win_folder as lr_win_folder
import lr_lib.gui.wrsp.top.top_allfiles as lr_top_allfiles
import lr_lib.gui.wrsp.top.top_encode as lr_top_encode
import lr_lib.gui.wrsp.top.top_pool as lr_top_pool
import lr_lib.gui.etc.sub_menu as lr_sub_menu
import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.help as lr_help


class WinMenu(lr_win_folder.WinFolder):
    """меню"""
    def __init__(self):
        lr_win_folder.WinFolder.__init__(self)

        self.menubar = tk.Menu(lr_vars.Tk)
        lr_vars.Tk.config(menu=self.menubar)

        self.set_menu()
        self.set_comboFiles_width()
        self.set_rclick_menu()

    def set_menu(self) -> None:
        """menubar"""
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Select Encode", command=lambda: lr_top_encode.TopEncoding(self))
        filemenu.add_command(label="Pools", command=lambda: lr_top_pool.TopPoolSetting(self))
        filemenu.add_command(label="Select Editor", command=self._select_editor)
        filemenu.add_command(label="Select Folder", command=self.change_folder_ask)
        filemenu.add_command(label="AllFiles list", command=lambda: lr_top_allfiles.TopFolder(self))
        filemenu.add_command(label="LoadRunner action.c", command=self.new_action_window)
        filemenu.add_command(label="Help", command=lambda *a: lr_vars.Logger.info(lr_help.CODE + '\n' + lr_help.HELP))
        filemenu.add_command(label="Exit", command=lr_vars.Tk.destroy)
        self.menubar.add_cascade(label="Menu", menu=filemenu)

    def _select_editor(self) -> None:
        """Select Editor"""
        __file = tk.filedialog.askopenfile()
        if __file:
            lr_vars.EDITOR['exe'] = __file.name

    def set_rclick_menu(self) -> None:
        """меню правой кнопки мыши"""
        lr_sub_menu.rClickbinder(self)  # все tk
        for widj in dir(self):
            with contextlib.suppress(Exception):
                self.bind_class(getattr(self, widj), sequence='<Button-3>', func=lr_sub_menu.rClicker, add='')
