# -*- coding: UTF-8 -*-
# основные виджеты (1) (2) (3) (6)

import time

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars_other
import lr_lib.gui.widj.lbrb5
import lr_lib.gui.wrsp.win_part_lbrb
import lr_lib.core.wrsp.files
import lr_lib.core.var.vars as lr_vars


class WinWidj(lr_lib.gui.wrsp.win_part_lbrb.WinPartsLbRb):
    """основные виджеты: (1) (2) (3) (6)"""
    cbxClearShowVar = tk.IntVar(value=lr_vars.cbxClearShowVar)  # перед (2), очищать центральный виджет текста
    cbxWrspClipboard = tk.IntVar(value=lr_vars.cbxWrspClipboard)  # после (2), копировать wrsp в буфер обмена
    cbxWrspAutoCreate = tk.IntVar(value=lr_vars.cbxWrspAutoCreate)  # после (2), выполнять (3)-(6)
    cbxNotepadWrsp = tk.IntVar(value=lr_vars.cbxNotepadWrsp)  # после (2), открывать web_reg_save_param в блокноте

    def __init__(self):
        lr_lib.gui.wrsp.win_part_lbrb.WinPartsLbRb.__init__(self)

        self.t0 = tk.Label(self.find_frame, text='?', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0,
                           foreground='grey')
        self.t01 = tk.Label(self.show_param_frame, text='?', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0,
                            foreground='grey')
        self.t02 = tk.Label(self.mid_frame, text='?', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0,
                            foreground='grey')
        self.t1 = tk.Label(self.find_frame, text='(1)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0,
                           foreground='brown')
        self.t2 = tk.Label(self.show_param_frame, text='(2)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0,
                           foreground='brown')
        self.t3 = tk.Label(self.mid_frame, text='(3)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0,
                           foreground='brown')

        # (1)
        self.comboParam = ttk.Combobox(self.find_frame, textvariable=lr_vars.VarParam, justify='center',
                                       font=lr_vars.DefaultFont, width=54)

        # (2)
        self.ButtonFindParamFiles = tk.Button(
            self.show_param_frame, text='поиск {param} в файлах ответов', font=lr_vars.DefaultFont + ' italic bold',
            padx=0, pady=0, command=lambda *a: lr_vars.Tk.after(0, self.get_files), background='orange')

        # (3)
        self.comboFiles = ttk.Combobox(self.mid_frame, state="readonly", justify='center', font=lr_vars.DefaultFont)

        # (6)
        self.t6 = tk.Label(self.mid_frame, text='(6)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0,
                           foreground='brown')

        #
        self.comboParam.bind("<KeyRelease-Return>", self.get_files)
        self.comboParam['values'] = self.param_hist_list
        self.comboParam.current(0)

        self.comboFiles.bind("<<ComboboxSelected>>", self.comboFiles_change)
        self.comboFiles['values'] = [self.no_files_text]
        self.comboFiles.current(0)
        return

    def get_files(self, *args, param=None, clipb=False, callback=None, action=None) -> None:
        """получить файлы с {param} (2)"""
        if param is not None:
            self.comboParam.set(param)

        self.show_frame_info_working()
        self.clear_before_find_param_files()

        param = self.comboParam.get()
        self.param_hist_list.insert(0, param)
        self.comboParam['values'] = self.param_hist_list

        with self.block():
            lr_vars.VarParam.set(param, set_file=False, action=action)  # получить файлы с {param}

        self.comboFiles['values'] = ([f['File']['Name'] for f in lr_vars.FilesWithParam] or [self.no_files_text])
        self.set_comboFiles_width()
        self.firstOrLastFile()

        if clipb or self.cbxWrspClipboard.get():
            self.clip_add(self.show_LR_Param(callback))
        elif self.cbxWrspAutoCreate.get():
            self.show_LR_Param(callback)

        self.last_frame['text'] = 'Файлы({files_all}->{param_files}) | ' \
                                  'Snapshot(все[{all_inf_min}:{all_inf_max}]={all_inf_len}->' \
                                  'поиск[{param_inf_min}:{param_inf_max}]={search_inf_len}->' \
                                  'найдено[{_param_inf_min}:{_param_inf_max}]={_param_inf_all}) | ' \
                                  'Найдено {param_all} param.'.format(**lr_vars.VarWrspDict.get())
        return

    def firstOrLastFile(self, *args) -> None:
        """выбрать первый/последный файл в (3)"""
        if (not lr_vars.FilesWithParam) or (not self.comboParam.get()):
            return
        # i = (len(self.comboFiles['values']) - 1) if lr_vars.VarFirstLastFile.get() else 0
        self.comboFiles.current(0)
        self.comboFiles_change()
        return

    def comboFiles_change(self, *args) -> None:
        """при смене комбо(3), читать файл, записать комбо(4), выбрать файл по умолчанию (3)"""
        name = self.comboFiles.get()
        lr_vars.VarFileName.set(name)
        part = lr_vars.VarPartNum.get()
        self.comboPartsFill()
        self.comboParts.set(part if part else 0)
        self.comboParts_change()
        lr_lib.gui.widj.tooltip.createToolTip(self.comboFiles, lr_lib.core.etc.other.file_string(lr_lib.core.wrsp.files.get_file_with_kwargs(
            lr_vars.FilesWithParam, Name=name)))
        return

    def comboPartsFill(self) -> None:
        """заполнить комбобокс (4)"""
        file = lr_vars.VarFile.get()
        if lr_vars.VarStrongSearchInFile.get():
            self.comboParts['values'] = file['Param']['Count_indexs']
        else:
            self.comboParts['values'] = list(range(file['Param']['Count']))
        lr_lib.gui.widj.tooltip.createToolTip(
            lr_vars.Window.comboFiles, lr_lib.core.etc.other.file_string(lr_lib.core.wrsp.files.get_file_with_kwargs(
                lr_vars.FilesWithParam, Name=file['File']['Name'])))
        return

    def show_LR_Param(self, callback=None) -> str:
        """показать web_reg_save_param (6)"""
        lr_vars.VarLB.set(self.LB.get())
        lr_vars.VarRB.set(self.RB.get())
        # с учетом редактирования LB/RB(5)
        web_reg_save_param = lr_lib.core.wrsp.param.create_web_reg_save_param(lr_lib.core.wrsp.param.wrsp_dict_creator())

        if web_reg_save_param:
            if self.cbxNotepadWrsp.get():
                lr_lib.core.etc.other.openTextInEditor(web_reg_save_param)
            if self.cbxWrspClipboard.get():
                self.clip_add(web_reg_save_param)
            if self.cbxClearShowVar.get():
                self.tk_text.delete(1.0, 'end')
            lr_vars.Logger.info('{s}\n{wrsp}\n{s}'.format(s=lr_vars.PRINT_SEPARATOR, wrsp=web_reg_save_param))
            if callback:  # highlight
                callback()
        return web_reg_save_param

    def set_comboFiles_width(self) -> None:
        """установка макс ширины комбо файлов(3)"""
        mf = max(len(f) for f in self.comboFiles['values'])
        mw = lr_vars.VarMaxComboFilesWidth.get()
        self.comboFiles.configure(width=(mf if (mf < mw) else mw), )
        return

    def clear_before_find_param_files(self) -> None:
        """очистка виджетов перед поиском"""
        self.LB.set('')
        self.RB.set('')
        lr_lib.gui.widj.lbrb5.LBRBText.set_label_text()
        self.comboFiles['values'] = [self.no_files_text]
        self.comboParts['values'] = [-1]
        self.comboFiles.current(0)
        self.comboParts.current(0)
        lr_vars.VarLB.set('')
        lr_vars.VarRB.set('')
        return

    def show_frame_info_working(self) -> None:
        """отображение всякой информации"""
        self.main_frame['text'] = '{} | {} | ParamClipBoardSearchHotKey[{}]'.format(
            lr_lib.core.var.vars_other.VarEncode.get(), time.strftime('%H:%M:%S'), lr_vars.FIND_PARAM_HOTKEY)
        self.last_frame['text'] = 'working ... {}'.format(lr_vars.VarFilesFolder.get())
        return
