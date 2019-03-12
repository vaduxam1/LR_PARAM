# -*- coding: UTF-8 -*-
# меню gui окна

import os
import tkinter as tk
from tkinter import filedialog

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.widj.setting
import lr_lib.gui.wrsp.top.top_encode
import lr_lib.gui.wrsp.top.top_pool
import lr_lib.gui.wrsp.win_folder


class WinMenu(lr_lib.gui.wrsp.win_folder.WinFolder):
    """
    меню
        main_window.Window
      + win_menu.WinMenu
        win_folder.WinFolder
        win_other.WinOther
        win_filesort.WinFileSort
        win_maxmin.WinMaxMin
        win_widj.WinWidj
        win_part_lbrb.WinPartsLbRb
        win_text.WinText
        win_block.WinBlock
        win_act.WinAct
        win_frame.WinFrame
        ttk.Frame
    """

    def __init__(self):
        lr_lib.gui.wrsp.win_folder.WinFolder.__init__(self)

        self.menubar = tk.Menu(lr_vars.Tk)
        lr_vars.Tk.config(menu=self.menubar)

        self.set_menu()
        self.set_comboFiles_width()
        self.set_rclick_menu()
        return

    def set_menu(self) -> None:
        """
        menubar
        """
        filemenu = tk.Menu(self.menubar, tearoff=0)

        cmd1 = lambda: lr_lib.gui.widj.setting.Setting(parent=self)
        filemenu.add_command(label="Setting", command=cmd1,)

        cmd2 = lambda: lr_lib.gui.wrsp.top.top_encode.TopEncoding(self)
        filemenu.add_command(label="Select Encode", command=cmd2,)

        cmd3 = lambda: lr_lib.gui.wrsp.top.top_pool.TopPoolSetting(self)
        filemenu.add_command(label="Pools", command=cmd3,)

        filemenu.add_command(label="Select Editor", command=self._select_editor,)

        filemenu.add_command(label="Select Folder", command=self.change_folder_ask,)

        cmd6 = lambda: lr_lib.gui.wrsp.top.top_allfiles.TopFolder(self)
        filemenu.add_command(label="AllFiles list", command=cmd6,)

        filemenu.add_command(label="LoadRunner action.c", command=self.new_action_window,)

        def cmd8() -> None:
            """help"""
            h = (lr_lib.etc.help.CODE + '\n' + lr_lib.etc.help.HELP)
            lr_vars.Logger.info(h)
            lr_vars.Tk.after(100, os.system, lr_vars.help_doc)  # after иначе не выводит Logger, тока открыто help_doc
            return
        filemenu.add_command(label="Help", command=cmd8,)

        filemenu.add_command(label="Exit", command=lr_vars.Tk.destroy,)

        self.menubar.add_cascade(label="Menu", menu=filemenu)
        return

    def _select_editor(self) -> None:
        """
        Select Editor
        """
        __file = tk.filedialog.askopenfile()
        if __file:
            lr_vars.EDITOR['exe'] = __file.name
        return

    def set_rclick_menu(self) -> None:
        """
        меню правой кнопки мыши
        """
        lr_lib.gui.etc.sub_menu.rClickbinder(self)  # все tk
        for widj in dir(self):
            try:
                ob = getattr(self, widj)
                self.bind_class(ob, sequence='<Button-3>', func=lr_lib.gui.etc.sub_menu.rClicker, add='')
            except tk.TclError as ex:
                pass
            continue
        return
