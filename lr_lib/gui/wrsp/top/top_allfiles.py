# -*- coding: UTF-8 -*-
# Toplevel окно файлов

import subprocess
import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars


class TopFolder(tk.Toplevel):
    """
    окно списка всех файлов
    """

    def __init__(self, action: 'lr_lib.gui.wrsp.main_window.Window', mx=150):
        tk.Toplevel.__init__(self)
        self.action = action

        self.transient(action)
        self.resizable(width=False, height=False)
        self.title('список всех файлов - %s' % len(lr_vars.AllFiles))

        comboAllFilesFolder = ttk.Combobox(self, foreground='grey', font=lr_vars.DefaultFont)

        cmd = lambda: subprocess.Popen([lr_vars.EDITOR['exe'], comboAllFilesFolder.get()])
        buttonAllFilesFolder = tk.Button(
            self, text='open', font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0, command=cmd,
        )

        ttip = lambda a: lr_lib.gui.widj.tooltip.createToolTip(
            comboAllFilesFolder, lr_lib.core.etc.other.file_string(lr_lib.core.wrsp.files.get_file_with_kwargs(
                lr_vars.AllFiles, FullName=comboAllFilesFolder.get()), deny=[])
        )

        comboAllFilesFolder.bind("<<ComboboxSelected>>", ttip)
        lr_lib.gui.widj.tooltip.createToolTip(buttonAllFilesFolder, 'открыть выбранный файл')
        t = 'список всех файлов, в которых производится поиск {param}\n\t# Window.folder_wind\n\t# lr_vars.AllFiles'
        lr_lib.gui.widj.tooltip.createToolTip(comboAllFilesFolder, t)

        files = list(f['File']['FullName'] for f in lr_vars.AllFiles)
        comboAllFilesFolder['values'] = files
        try:
            m = max(len(f) for f in files)
            if m < mx:
                mx = m
            comboAllFilesFolder.configure(width=mx)
        except Exception as ex:
            pass

        buttonAllFilesFolder.pack()
        comboAllFilesFolder.pack()
        lr_lib.gui.etc.gui_other.center_widget(self)
        return
