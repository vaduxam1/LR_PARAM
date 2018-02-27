# -*- coding: UTF-8 -*-
# Toplevel окно файлов

import contextlib
import subprocess

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.files as lr_files
import lr_lib.core.etc.other as lr_other
import lr_lib.gui.etc.gui_other as lr_gui_other
import lr_lib.gui.widj.tooltip as lr_tooltip


class TopFolder(tk.Toplevel):
    """окно списка всех файлов"""
    def __init__(self, action, mx=150):
        tk.Toplevel.__init__(self)
        self.action = action

        self.transient(action)
        self.resizable(width=False, height=False)
        self.title('список всех файлов - %s' % len(lr_vars.AllFiles))

        comboAllFilesFolder = ttk.Combobox(self, foreground='grey', font=lr_vars.DefaultFont)
        buttonAllFilesFolder = tk.Button(
            self, text='open', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0,
            command=lambda: subprocess.Popen([lr_vars.EDITOR['exe'], comboAllFilesFolder.get()]))

        ttip = lambda a: lr_tooltip.createToolTip(comboAllFilesFolder, lr_other.file_string(
            lr_files.get_file_with_kwargs(lr_vars.AllFiles, FullName=comboAllFilesFolder.get()), deny=[]))

        comboAllFilesFolder.bind("<<ComboboxSelected>>", ttip)
        lr_tooltip.createToolTip(buttonAllFilesFolder, 'открыть выбранный файл')
        lr_tooltip.createToolTip(comboAllFilesFolder, 'список всех файлов, в которых производится поиск {param}'
                                                      '\n\t# Window.folder_wind\n\t# lr_vars.AllFiles')

        files = list(f['File']['FullName'] for f in lr_vars.AllFiles)
        comboAllFilesFolder['values'] = files
        with contextlib.suppress(Exception):
            m = max(len(f) for f in files)
            if m < mx:
                mx = m
            comboAllFilesFolder.configure(width=mx)

        buttonAllFilesFolder.pack()
        comboAllFilesFolder.pack()
        lr_gui_other.center_widget(self)

