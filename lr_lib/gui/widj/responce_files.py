# -*- coding: UTF-8 -*-
# окно файлов ответов, для i_num-snapshot

import os
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog

import lr_lib.gui.etc.gui_other

import lr_lib.core.etc.other as lr_other
import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.files as lr_files


class RespFiles(tk.Toplevel):
    '''окно файлов ответов, для i_num-snapshot'''
    def __init__(self, widget, i_num, folder_record, folder_response):
        super().__init__(padx=0, pady=0)
        self.widget = widget
        self.i_num = i_num
        self.transient(self.widget)
        self.inf_file = 't{i}.inf'.format(i=i_num)
        self.title('окно файлов snapshot=' + self.inf_file)
        lr_lib.gui.etc.gui_other.center_widget(self)

        self.folder_record = folder_record
        self.folder_response = folder_response

        self.response_widj_creator(folder_record, desc='файлы при записи')
        self.response_widj_creator(folder_response, desc='файлы при воспроизведении')

    def combo_select(self, ent: tk.Entry, folder: str, cbx_var: tk.BooleanVar):
        full_name = os.path.join(folder, ent.get())
        if cbx_var.get():
            lr_other._openTextInEditor(full_name)

        file_dt = lr_files.file_dict_creator(
            ent.get(), full_name, inf_num=0, enc=lr_vars.VarEncode.get(), inf_key='', allow_deny=True, set_statistic=True)
        del file_dt['Param']
        del file_dt['Snapshot']

        lr_tooltip.createToolTip(ent, lr_other.file_string(file_dt))

    def response_widj_creator(self, folder: str, desc='', mx=40) -> None:
        '''виджеты для окна файлов snapshot'''
        text = '{desc}\n{folder}'.format(desc=desc, folder=folder)

        lab = tk.Label(self, text=desc)
        btn = tk.Button(self, text='folder', command=lambda: self.select_folder(folder))
        lr_tooltip.createToolTip(btn, 'выбор папки с файлами\nвнутри должен быть файл t{}.inf'.format(self.i_num))

        cbx_var = tk.BooleanVar(value=True)
        cbx = tk.Checkbutton(self, text='open', variable=cbx_var)
        lr_tooltip.createToolTip(cbx, 'не открывать файл, при выборе в комбобоксе')

        ent = ttk.Combobox(self, justify='center', background=lr_vars.Background, font=lr_vars.DefaultFont)

        files = list(lr_other.get_files_names(folder, self.i_num))
        if not files:
            return
        ent['values'] = files
        ent.bind("<<ComboboxSelected>>", lambda *a: self.combo_select(ent, folder, cbx_var))

        m = max(map(len, ent['values']))
        if m < mx:
            m = mx
        ent.config(width=m)
        lr_tooltip.createToolTip(ent, text)

        cbx.pack()
        btn.pack()
        lab.pack()
        ent.pack()

    def select_folder(self, folder: str) -> None:
        directory = filedialog.askdirectory()
        if directory:
            if self.folder_record == folder:
                self.folder_record, self.folder_response = (directory, self.folder_response)
            else:
                self.folder_record, self.folder_response = (self.folder_record, directory)

        self.destroy()
        RespFiles(self.widget, self.i_num, self.folder_record, self.folder_response)
