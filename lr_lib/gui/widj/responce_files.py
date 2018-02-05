# -*- coding: UTF-8 -*-
# окно файлов ответов, для i_num-snapshot

import os
import tkinter as tk
import tkinter.ttk as ttk

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
        self.title('окно файлов snapshot=t{i}.inf'.format(i=i_num))
        lr_lib.gui.etc.gui_other.center_widget(self)

        self.response_widj_creator(folder_record, i_num, desc='файлы при записи')
        self.response_widj_creator(folder_response, i_num, desc='файлы при воспроизведении')

    def combo_select(self, ent: tk.Entry, folder: str, cbx_var: tk.BooleanVar):
        full_name = os.path.join(folder, ent.get())
        if cbx_var.get():
            lr_other._openTextInEditor(full_name)

        file_dt = lr_files.file_dict_creator(
            ent.get(), full_name, 0, enc=lr_vars.VarEncode.get(), inf_key='', allow_deny=True, set_statistic=True)

        lr_tooltip.createToolTip(ent, lr_other.file_string(file_dt))

    def response_widj_creator(self, folder: str, i_num: int, desc='', mx=40) -> None:
        '''виджеты для окна файлов snapshot'''
        text = '{desc}\n{folder}'.format(desc=desc, folder=folder)

        lab = tk.Label(self, text=text)

        cbx_var = tk.BooleanVar(value=True)
        cbx = tk.Checkbutton(self, text='open', variable=cbx_var)

        ent = ttk.Combobox(self, justify='center', background=lr_vars.Background, font=lr_vars.DefaultFont)

        files = list(lr_other.get_files_names(folder, i_num))
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
        lab.pack()
        ent.pack()