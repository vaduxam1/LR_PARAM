# -*- coding: UTF-8 -*-
# окно файлов ответов, для i_num-snapshot

import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_other


class RespFiles(tk.Toplevel):
    """окно файлов ответов, для i_num-snapshot"""

    def __init__(self, widget, i_num: int, folder_record: str, folder_response: str):
        super().__init__(padx=0, pady=0)
        self.widget = widget
        self.i_num = i_num
        self.transient(self.widget)
        self.inf_file = 't{i}.inf'.format(i=i_num)
        self.title('Snapshot=' + self.inf_file)
        lr_lib.gui.etc.gui_other.center_widget(self)

        self.folder_record = folder_record
        self.folder_response = folder_response

        self.resp_widj = []
        self.response_widj_creator(folder_record, desc='файлы при записи', side='top')
        self.response_widj_creator(folder_response, desc='файлы при воспроизведении', side='bottom')
        return

    def combo_select(self, ent: tk.Entry, folder: str, cbx_var: tk.BooleanVar):
        full_name = os.path.join(folder, ent.get())
        if cbx_var.get():
            lr_lib.core.etc.other._openTextInEditor(full_name)

        file_dt = lr_lib.core.wrsp.files.file_dict_creator(
            ent.get(), full_name, inf_num=0, enc=lr_lib.core.var.vars_other.VarEncode.get(), inf_key='', deny=True,
            stats=True)
        del file_dt['Param']
        del file_dt['Snapshot']

        lr_lib.gui.widj.tooltip.createToolTip(ent, lr_lib.core.etc.other.file_string(file_dt))
        return

    def response_widj_creator(self, folder: str, desc='', side='bottom', w1=30, w2=100) -> None:
        """виджеты для окна файлов snapshot"""
        text = '{desc}\n{folder}'.format(desc=desc, folder=folder)

        lab = tk.LabelFrame(self, text=desc, font='Arial 7')
        btn = tk.Button(lab, text='folder', command=lambda: self.select_folder(folder), font='Arial 7')
        lr_lib.gui.widj.tooltip.createToolTip(btn, 'выбор папки с файлами\nвнутри должен быть файл {i}\n{d}'.format(
            i=self.inf_file, d=folder))

        cbx_var = tk.BooleanVar(value=True)
        cbx = tk.Checkbutton(lab, text='', variable=cbx_var, font='Arial 7')
        lr_lib.gui.widj.tooltip.createToolTip(cbx, 'открывать файл, при выборе в комбобоксе')

        def files_cmb_set(files=tuple(lr_lib.core.etc.other.get_files_names(folder, self.i_num))) -> None:
            """записать файлы в files_cmb"""
            if deny_cbx_var.get():  # отбраковать "вероятно ненужные" файлы
                files = list(filter(lr_lib.core.wrsp.files.is_responce_file, files))
            files_cmb['values'] = files
            return

        deny_cbx_var = tk.BooleanVar(value=True)
        deny_cbx = tk.Checkbutton(lab, text='', variable=deny_cbx_var, command=files_cmb_set, font='Arial 7')
        lr_lib.gui.widj.tooltip.createToolTip(deny_cbx, 'отбраковать "вероятно ненужные" файлы')

        files_cmb = ttk.Combobox(lab, background=lr_lib.core.var.vars_highlight.Background, font='Arial 7')
        files_cmb_set()
        files_cmb.bind("<<ComboboxSelected>>", lambda *a: self.combo_select(files_cmb, folder, cbx_var))
        lr_lib.gui.widj.tooltip.createToolTip(files_cmb, text)

        def get_inf_files() -> iter((str,)):
            """все inf файлы директории"""
            folder_files = next(os.walk(folder))
            for file in folder_files[2]:
                num = lr_lib.core.wrsp.files.get_inf_file_num(file)
                if num:
                    yield file
                continue
            return

        def set_inf(*a) -> None:
            """новый snapshot"""
            self.i_num = int(''.join(filter(str.isnumeric, inf_var.get())))
            RespFiles(self.widget, self.i_num, self.folder_record, self.folder_response)
            inf_var.set(self.inf_file)
            return

        inf_var = tk.StringVar(value=self.inf_file)
        inf_cmb = ttk.Combobox(lab, background=lr_lib.core.var.vars_highlight.Background, font='Arial 7',
                               textvariable=inf_var)
        inf_cmb['values'] = list(sorted(get_inf_files(), key=lr_lib.core.etc.other.numericalSort))
        inf_cmb.bind("<<ComboboxSelected>>", set_inf)
        inf_cmb.config(width=max(len(i) for i in (inf_cmb['values'] or [''])))
        inf = os.path.join(folder, self.inf_file)
        if os.path.isfile(inf):
            with open(inf) as f:
                lr_lib.gui.widj.tooltip.createToolTip(inf_cmb, 'сменить snapshot\n{}'.format(f.read()), )

        lab.pack(side=side)
        files_cmb.pack(side='top')
        btn.pack(side='left')
        cbx.pack(side='left')
        deny_cbx.pack(side='left')
        inf_cmb.pack(side='bottom')

        # width
        self.resp_widj.append((lab, cbx, btn, files_cmb, inf_cmb, deny_cbx, deny_cbx_var, inf_var, cbx_var, folder))
        w = max(len(e[3]['values']) for e in self.resp_widj)
        if w < w1:
            w = w1
        elif w > w2:
            w = w2
        for i in range(len(self.resp_widj)):
            self.resp_widj[i][3].config(width=w)
            continue
        return

    def select_folder(self, folder: str) -> None:
        """ноавя директория snapshot"""
        directory = filedialog.askdirectory()
        if not directory:
            return

        if self.folder_record == folder:
            (self.folder_record, self.folder_response) = (directory, self.folder_response)
        else:
            (self.folder_record, self.folder_response) = (self.folder_record, directory)

        RespFiles(self.widget, self.i_num, self.folder_record, self.folder_response)
        return
