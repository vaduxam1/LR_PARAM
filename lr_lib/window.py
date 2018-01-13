# -*- coding: UTF-8 -*-
# основное gui окно

import contextlib
import collections
import itertools
import string
import subprocess
import time
import tkinter as tk
import tkinter.ttk as ttk

from lr_lib import (
    defaults,
    files as lr_files,
    param as lr_param,
    other as lr_other,
    window_action as lr_action,
    window_lib as lr_wlib,
    window_widj as lr_widj,
    pool as lr_pool,
    help as lr_help,
    logger as lr_log,
)


class Window(ttk.Frame):
    cbxClearShowVar = tk.IntVar(value=defaults.cbxClearShowVar)  # перед (2), очищать центральный виджет текста
    cbxWrspClipboard = tk.IntVar(value=defaults.cbxWrspClipboard)  # после (2), копировать web_reg_save_param в буфер обмена
    cbxWrspAutoCreate = tk.IntVar(value=defaults.cbxWrspAutoCreate)  # после (2), выполнять (3)-(6)
    cbxNotepadWrsp = tk.IntVar(value=defaults.cbxNotepadWrsp)  # после (2), открывать web_reg_save_param в блокноте

    def __init__(self, action=True, auto_param_creator=False):
        defaults.Window = self
        self._block_ = None  # принудительно блокировать виджеты

        super().__init__(defaults.Tk, padding="0 0 0 0")
        defaults.Tk.protocol("WM_DELETE_WINDOW", self.on_closing)
        defaults.Tk.geometry('{}x{}'.format(*defaults._Tk_WIND_SIZE))
        defaults.Tk.option_add("*TCombobox*Listbox*Background", defaults.Background)
        # "масштабирование" виджетов окна
        defaults.Tk.grid_rowconfigure(0, weight=1)
        defaults.Tk.grid_columnconfigure(0, weight=1)
        defaults.Tk.title(defaults.VERSION)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=tk.NSEW)

        self.action_windows = collections.OrderedDict()  # спросить, перед выходом, если открыты action.c окна

        self.no_param_text = ''
        self.no_files_text = ''
        self.param_hist_list = [self.no_param_text]

        # создать виджеты
        self.main_frame = tk.LabelFrame(
            self, bd=2, labelanchor=tk.N, relief='groove', padx=0, pady=0, font=defaults.DefaultFont)
        self.mid_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.find_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.show_param_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.last_frame = tk.LabelFrame(
            self, labelanchor=tk.S, bd=1, relief='groove', padx=0, pady=0, font=defaults.DefaultFont)

        self.sortKey1 = ttk.Combobox(
            self.last_frame, textvariable=defaults.VarFileSortKey1, justify='center',
            font=defaults.DefaultFont + ' italic', style="BW.TButton", width=10)
        self.sortKey2 = ttk.Combobox(
            self.last_frame, textvariable=defaults.VarFileSortKey2, justify='center',
            font=defaults.DefaultFont + ' italic', style="BW.TButton")

        # text
        self.tk_text = lr_widj.HighlightText(
            self, foreground='grey', background=defaults.Background, wrap=tk.NONE, height=10, padx=0, pady=0, undo=True,

        )
        self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
        self.tk_text.configure(
            yscrollcommand=self.text_scrolly.set, xscrollcommand=self.text_scrollx.set, bd=0, padx=0, pady=0)

        # (1)
        self.t1 = tk.Label(
            self.find_frame, text='(1)', font=defaults.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.t0 = tk.Label(
            self.find_frame, text='?', font=defaults.DefaultFont + ' italic', padx=0, pady=0, foreground='grey')
        self.t01 = tk.Label(
            self.show_param_frame, text='?', font=defaults.DefaultFont + ' italic', padx=0, pady=0, foreground='grey')
        self.t02 = tk.Label(
            self.mid_frame, text='?', font=defaults.DefaultFont + ' italic', padx=0, pady=0, foreground='grey')
        self.comboParam = ttk.Combobox(
            self.find_frame, textvariable=defaults.VarParam, justify='center', font=defaults.DefaultFont, width=54)
        self.cbxFirstLastFile = tk.Checkbutton(
            self.mid_frame, variable=defaults.VarFirstLastFile, text='last',
            font=defaults.DefaultFont + ' italic', padx=0, pady=0, command=self.firstOrLastFile)
        self.StrongSearchInFile_cbx = tk.Checkbutton(
            self.mid_frame, variable=defaults.VarStrongSearchInFile, padx=0, pady=0, text='strong',
            font=defaults.DefaultFont + ' italic')

        self.actionButton = tk.Button(
            self.find_frame, text=' action.c  editor ', font=defaults.DefaultFont + ' italic bold', padx=0,
            pady=0, command=lr_action.ActionWindow, relief='ridge', background='orange')

        # (2)
        self.t2 = tk.Label(
            self.show_param_frame, text='(2)', font=defaults.DefaultFont + ' italic bold', padx=0, pady=0,
            foreground='brown')
        self.ButtonFindParamFiles = tk.Button(
            self.show_param_frame, text='поиск {param} в файлах ответов', font=defaults.DefaultFont + ' italic bold',
            padx=0, pady=0, command=lambda *a: defaults.Tk.after(0, self.get_files), background='orange')
        self.max_inf = ttk.Combobox(
            self.show_param_frame, width=10, textvariable=defaults.VarSearchMaxInf,
            justify='center', foreground='grey', font=defaults.DefaultFont, style="BW.TButton")

        self.min_inf = ttk.Combobox(
            self.show_param_frame, width=10, textvariable=defaults.VarSearchMinInf,
            justify='center', foreground='grey', font=defaults.DefaultFont, style="BW.TButton")

        # (3)
        self.t3 = tk.Label(
            self.mid_frame, text='(3)', font=defaults.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.comboFiles = ttk.Combobox(
            self.mid_frame, state="readonly", justify='center', font=defaults.DefaultFont, style="BW.TButton")

        # (4)
        self.t4 = tk.Label(
            self.mid_frame, text='(4)', font=defaults.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.comboParts = ttk.Combobox(
            self.mid_frame, justify='center', width=5, style="BW.TButton", font=defaults.DefaultFont + ' bold')

        # (5) LB/RB
        self.LB = lr_widj.LBRBText('LB', self)
        self.RB = lr_widj.LBRBText('RB', self)
        self.last_frameCbx1 = ttk.Label(self.LB.label_info, padding="0 0 0 0")
        self.last_frameCbx2 = ttk.Label(self.RB.label_info, padding="0 0 0 0")

        @lr_pool.T_POOL_execute_decotator
        def lr_note(ob) -> None:
            lr_log.openTextInEditor(ob.get())

        self.t5l = tk.Label(
            self, text='(5)', font=defaults.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.t5r = tk.Label(
            self, text='(5)', font=defaults.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')

        SplitList = (
            defaults.SplitList, defaults.SplitList0, defaults.SplitList1, defaults.SplitList2, defaults.SplitList_3,
            list(string.whitespace), 'list(string.ascii_letters)', 'list(string.digits)', 'list(string.punctuation)',
        )
        SplitList = tuple(str(l) for l in SplitList)

        # ---LB
        self.ButtonNewLB = tk.Button(
            self.last_frameCbx1, text='->', command=self.comboParts_change, font=defaults.DefaultFont + ' italic',
            width=2, padx=0, pady=0)
        self.LBcbx_return = tk.Checkbutton(
            self.last_frameCbx1, variable=defaults.VarReturnLB, text='\\n', font=defaults.DefaultFont + ' italic',
            command=self.comboParts_change, padx=0, pady=0, anchor=tk.S)
        self.LBcbx_rus = tk.Checkbutton(
            self.last_frameCbx1, variable=defaults.VarRusLB, text='ascii', font=defaults.DefaultFont + ' italic',
            command=self.comboParts_change, padx=0, pady=0)

        self.lb_split_label = tk.LabelFrame(self.last_frameCbx1, bd=1, padx=0, pady=0, relief='ridge')

        def spl_cbx_cmd_lb(*a) -> None:
            if defaults.VarSplitListLB.get():
                self.LBent_SplitList.configure(state='normal')
                self.LBSpinSplitList.configure(state='normal')
                self.LbB1Cbx.configure(state='normal')
                self.LbB2Cbx.configure(state='normal')
            else:
                self.LBent_SplitList.configure(state='disabled')
                self.LBSpinSplitList.configure(state='disabled')
                self.LbB1Cbx.configure(state='disabled')
                self.LbB2Cbx.configure(state='disabled')
            self.comboParts_change()

        self.LBcbx_SplitList = tk.Checkbutton(
            self.lb_split_label, variable=defaults.VarSplitListLB, text='eval', font=defaults.DefaultFont + ' bold',
            command=spl_cbx_cmd_lb, padx=0, pady=0)
        self.LBent_SplitList = ttk.Combobox(self.lb_split_label, font=defaults.DefaultFont, width=10)
        self.LBent_SplitList['values'] = list(SplitList)
        self.LBent_SplitList.current(0)
        self.LBSpinSplitList = tk.Spinbox(
            self.lb_split_label, from_=0, to=100, textvariable=defaults.VarSplitListNumLB, width=2,
            font=defaults.DefaultFont, command=self.comboParts_change)

        self.max_lb = tk.Entry(
            self.last_frameCbx1, width=5, textvariable=defaults.VarMaxLenLB, justify='center',
            foreground='grey', background=defaults.Background, font=defaults.DefaultFont + ' italic')
        self.spin_LB_height = tk.Spinbox(
            self.last_frameCbx1, from_=1, to=99, textvariable=self.LB.heightVar, width=2,
            command=self.LB.set_height, font=defaults.DefaultFont + ' italic', background=defaults.Background)
        self.ButtonLB_note = tk.Button(
            self.last_frameCbx1, text='edit', command=lambda: lr_note(self.LB), width=3,
            font=defaults.DefaultFont + ' italic', padx=0, pady=0)
        self.partNumEmptyLbNext = tk.Checkbutton(
            self.last_frameCbx1, variable=defaults.VarPartNumEmptyLbNext,
            text='strip', font=defaults.DefaultFont + ' bold', padx=0, pady=0)
        self.partNumDenyLbNext = tk.Checkbutton(
            self.last_frameCbx1, variable=defaults.VarPartNumDenyLbNext,
            text='deny', font=defaults.DefaultFont + ' bold', padx=0, pady=0)

        self.LbB1Cbx = tk.Checkbutton(
            self.lb_split_label, variable=defaults.VarLbB1,
            text='{', font=defaults.DefaultFont, padx=0, pady=0)
        self.LbB2Cbx = tk.Checkbutton(
            self.lb_split_label, variable=defaults.VarLbB2,
            text='[', font=defaults.DefaultFont, padx=0, pady=0)
        self.LbRstripCbx = tk.Checkbutton(
            self.last_frameCbx1, variable=defaults.VarLbLstrip,
            text='lstrip', font=defaults.DefaultFont, padx=0, pady=0)
        self.LbEndCbx = tk.Checkbutton(
            self.last_frameCbx1, variable=defaults.VarLEnd,
            text='end', font=defaults.DefaultFont, padx=0, pady=0)

        # ---RB
        self.ButtonNewRB = tk.Button(
            self.last_frameCbx2, text='->', command=self.comboParts_change,
            font=defaults.DefaultFont + ' italic', width=2, padx=0, pady=0)
        self.RBcbx_return = tk.Checkbutton(
            self.last_frameCbx2, variable=defaults.VarReturnRB, text='\\n',
            font=defaults.DefaultFont + ' italic', command=self.comboParts_change, padx=0, pady=0)
        self.RBcbx_rus = tk.Checkbutton(
            self.last_frameCbx2, variable=defaults.VarRusRB, text='ascii',
            font=defaults.DefaultFont + ' italic', command=self.comboParts_change, padx=0, pady=0)

        self.rb_split_label = tk.LabelFrame(self.last_frameCbx2, bd=1, padx=0, pady=0, relief='ridge')

        def spl_cbx_cmd_rb(*a) -> None:
            if defaults.VarSplitListRB.get():
                self.RBent_SplitList.configure(state='normal')
                self.RBSpinSplitList.configure(state='normal')
                self.RbB1Cbx.configure(state='normal')
                self.RbB2Cbx.configure(state='normal')
            else:
                self.RBent_SplitList.configure(state='disabled')
                self.RBSpinSplitList.configure(state='disabled')
                self.RbB1Cbx.configure(state='disabled')
                self.RbB2Cbx.configure(state='disabled')
            self.comboParts_change()

        self.RBcbx_SplitList = tk.Checkbutton(
            self.rb_split_label, variable=defaults.VarSplitListRB, text='eval',
            font=defaults.DefaultFont + ' bold', command=spl_cbx_cmd_rb, padx=0, pady=0)
        self.RBent_SplitList = ttk.Combobox(self.rb_split_label, font=defaults.DefaultFont, width=10)
        self.RBent_SplitList['values'] = list(SplitList)
        self.RBent_SplitList.current(0)
        self.RBSpinSplitList = tk.Spinbox(
            self.rb_split_label, from_=0, to=100, textvariable=defaults.VarSplitListNumRB,
            width=2, font=defaults.DefaultFont, command=self.comboParts_change)

        self.max_rb = tk.Entry(
            self.last_frameCbx2, width=5, textvariable=defaults.VarMaxLenRB, justify='center',
            foreground='grey', background=defaults.Background, font=defaults.DefaultFont + ' italic')
        self.partNumEmptyRbNext = tk.Checkbutton(
            self.last_frameCbx2, variable=defaults.VarPartNumEmptyRbNext,
            text='strip', font=defaults.DefaultFont + ' bold', padx=0, pady=0)
        self.partNumDenyRbNext = tk.Checkbutton(
            self.last_frameCbx2, variable=defaults.VarPartNumDenyRbNext,
            text='deny', font=defaults.DefaultFont + ' bold', padx=0, pady=0)
        self.spin_RB_height = tk.Spinbox(
            self.last_frameCbx2, from_=1, to=99, textvariable=self.RB.heightVar, width=2,
            command=self.RB.set_height, font=defaults.DefaultFont + ' italic', background=defaults.Background)
        self.ButtonRB_note = tk.Button(
            self.last_frameCbx2, text='edit', command=lambda: lr_note(self.RB), width=3,
            font=defaults.DefaultFont + ' italic', padx=0, pady=0)

        self.RbB1Cbx = tk.Checkbutton(
            self.rb_split_label, variable=defaults.VarRbB1,
            text='}', font=defaults.DefaultFont, padx=0, pady=0)
        self.RbB2Cbx = tk.Checkbutton(
            self.rb_split_label, variable=defaults.VarRbB2,
            text=']', font=defaults.DefaultFont, padx=0, pady=0)
        self.RbRstripCbx = tk.Checkbutton(
            self.last_frameCbx2, variable=defaults.VarRbRstrip,
            text='rstrip', font=defaults.DefaultFont, padx=0, pady=0)
        self.RbEndCbx = tk.Checkbutton(
            self.last_frameCbx2, variable=defaults.VarREnd,
            text='end', font=defaults.DefaultFont, padx=0, pady=0)

        # (6)
        self.t6 = tk.Label(
            self.mid_frame, text='(6)', font=defaults.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.ButtonShowParam = tk.Button(
            self.mid_frame, text='сформировать web_reg_save_param ', command=self.show_LR_Param, padx=0, pady=0,
            font=defaults.DefaultFont + ' bold', background='orange')

        self.cbxClipboard = tk.Checkbutton(
            self.mid_frame, variable=self.cbxWrspClipboard, text='clipboard', font=defaults.DefaultFont + ' italic',
            padx=0, pady=0)
        self.filesStats_cbx = tk.Checkbutton(
            self.last_frame, variable=defaults.VarAllFilesStatistic, padx=0, pady=0, text='stats',
            font=defaults.DefaultFont + ' italic', command=self.set_folder)
        self.cbxClearShow = tk.Checkbutton(
            self.mid_frame, variable=self.cbxClearShowVar, text='clear', font=defaults.DefaultFont + ' italic',
            padx=0, pady=0)
        self.cbxAutoShowParam = tk.Checkbutton(
            self.show_param_frame, variable=self.cbxWrspAutoCreate, text='auto', font=defaults.DefaultFont + ' italic',
            padx=0, pady=0)
        self.cbxAutoNoteParam = tk.Checkbutton(
            self.mid_frame, variable=self.cbxNotepadWrsp, text='notepad', font=defaults.DefaultFont + ' italic',
            padx=0, pady=0)
        self.cbxFileNamesNumsShow = tk.Checkbutton(
            self.show_param_frame, variable=defaults.VarFileNamesNumsShow, text='name',
            font=defaults.DefaultFont + ' italic', padx=0, pady=0)
        self.cbxPopupWindow = tk.Checkbutton(
            self.last_frame, variable=defaults.VarShowPopupWindow, text='Window', padx=0, pady=0, background='orange',
            font=defaults.DefaultFont + ' italic bold')

        def force_unblock(*a) -> None:
            self._block_ = False
            self._block(False)

        self.unblock = tk.Button(
            self.last_frame, text='unblock', font=defaults.DefaultFont + ' bold', padx=0, pady=0, command=force_unblock)
        self.ButtonClearDown = tk.Button(
            self.last_frame, text='clearW', command=self.clear, font=defaults.DefaultFont + ' italic', padx=0, pady=0)
        self.ButtonClearUp = tk.Button(
            self.last_frame, text='clearT', command=lambda: self.tk_text.delete(0.0, 'end'),
            font=defaults.DefaultFont + ' italic', padx=0, pady=0)
        self.ButtonNote = tk.Button(
            self.last_frame, text='text', command=lambda: lr_log.openTextInEditor(self.tk_text.get('1.0', tk.END)),
            font=defaults.DefaultFont + ' italic', padx=0, pady=0)
        self.ButtonLog = tk.Button(
            self.last_frame, text='log', font=defaults.DefaultFont + ' italic', padx=0, pady=0,
            command=lambda: subprocess.Popen([defaults.EDITOR['exe'], defaults.logFullName]))

        @lr_pool.T_POOL_execute_decotator
        def editor_fn(*a) -> None:
            '''открыть в editor'''
            subprocess.Popen(
                [defaults.EDITOR['exe'], lr_files.get_file_with_kwargs(defaults.FilesWithParam)['File']['FullName']])

        self.ButtonParamFileOpen = tk.Button(
            self.last_frame, text='file(3)', font=defaults.DefaultFont + ' bold', padx=0, pady=0, command=editor_fn)
        self.Button_change_folder = tk.Button(
            self.last_frame, text='Folder', padx=0, pady=0, command=self.change_folder_ask,
            font=defaults.DefaultFont + ' italic bold')
        self.change_folder_cbx = tk.Checkbutton(
            self.last_frame, variable=defaults.VarIsInfFiles, padx=0, pady=0, font=defaults.DefaultFont + ' italic',
            command=self.set_folder, text='inf')
        self.deny_file_cbx = tk.Checkbutton(
            self.last_frame, variable=defaults.VarAllowDenyFiles, padx=0, pady=0, font=defaults.DefaultFont + ' italic',
            command=self.set_folder, text='deny_ext')
        self.spin_toolTipTimeout = tk.Entry(
            self.last_frame, textvariable=defaults.VarToolTipTimeout, width=4, font=defaults.DefaultFont + ' italic')
        self.cbxOrdVersion = tk.Checkbutton(
            self.mid_frame, variable=defaults.VarOrdVersion, padx=0, pady=0, font=defaults.DefaultFont, text='ord')

        log_vals = list(defaults.loggingLevels.keys())
        self.comboLogger = ttk.Combobox(
            self.last_frame, textvariable=defaults.VarWindowLogger, justify='center', font=defaults.DefaultFont,
            width=max(len(k) for k in log_vals), style="BW.TButton")
        self.comboLogger['values'] = log_vals

        self.main_frame.grid(row=2, column=0, sticky=tk.NS, padx=0, pady=0)
        self.find_frame.grid(row=4, column=0, sticky=tk.NS, padx=0, pady=0)
        self.show_param_frame.grid(row=6, column=0, sticky=tk.NS, padx=0, pady=0)
        self.mid_frame.grid(row=7, column=0, sticky=tk.NS, padx=0, pady=0)
        self.last_frameCbx1.grid(row=13, column=0, sticky=tk.NS, padx=0, pady=0)
        self.last_frameCbx2.grid(row=18, column=0, sticky=tk.NS, padx=0, pady=0)
        self.last_frame.grid(row=26, column=0, sticky=tk.N, padx=0, pady=0)

        self.t0.grid(row=1, column=20, sticky=tk.E, padx=0, pady=0)
        self.t01.grid(row=1, column=21, sticky=tk.E, padx=0, pady=0)
        self.t1.grid(row=1, column=0, sticky=tk.E, padx=0, pady=0)
        self.t2.grid(row=1, column=14, sticky=tk.E, padx=0, pady=0)
        self.t3.grid(row=4, column=1, sticky=tk.E, padx=0, pady=0)
        self.t4.grid(row=4, column=6, sticky=tk.W, padx=0, pady=0)
        self.t02.grid(row=4, column=6, sticky=tk.E, padx=0, pady=0)
        self.t6.grid(row=5, column=1, sticky=tk.E, padx=0, pady=0)

        self.tk_text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
        self.text_scrolly.grid(row=0, column=1, sticky=tk.NS, padx=0, pady=0)
        self.text_scrollx.grid(row=1, column=0, sticky=tk.EW, padx=0, pady=0)

        self.sortKey1.grid(row=2, column=5, sticky=tk.EW, padx=0, pady=0, columnspan=2)
        self.sortKey2.grid(row=2, column=7, sticky=tk.EW, padx=0, pady=0, columnspan=200)
        self.comboLogger.grid(row=1, column=75, sticky=tk.N, padx=0, pady=0)
        self.spin_toolTipTimeout.grid(row=1, column=80, sticky=tk.N, padx=0, pady=0)
        self.cbxPopupWindow.grid(row=1, column=76, sticky=tk.E, padx=0, pady=0)
        self.unblock.grid(row=1, column=74, sticky=tk.E, padx=0, pady=0)
        self.Button_change_folder.grid(row=1, column=100, sticky=tk.E, padx=0, pady=0)

        self.min_inf.grid(row=1, column=15, sticky=tk.N, padx=0, pady=0)
        self.ButtonFindParamFiles.grid(row=1, column=16, sticky=tk.EW, padx=0, pady=0)
        self.cbxFileNamesNumsShow.grid(row=1, column=19, sticky=tk.E, padx=0, pady=0)
        self.max_inf.grid(row=1, column=17, sticky=tk.N, padx=0, pady=0)
        self.cbxFirstLastFile.grid(row=4, column=3, sticky=tk.W, padx=0, pady=0)
        self.StrongSearchInFile_cbx.grid(row=4, column=4, sticky=tk.W, padx=0, pady=0)
        self.comboParts.grid(row=4, column=5, sticky=tk.E, padx=0, pady=0)

        self.actionButton.grid(row=1, column=19, sticky=tk.N, padx=0, pady=0)

        self.ButtonShowParam.grid(row=5, column=2, sticky=tk.EW, padx=0, pady=0)
        self.comboFiles.grid(row=4, column=2, sticky=tk.EW, padx=0, pady=0)
        self.comboParam.grid(row=1, column=1, sticky=tk.EW, padx=0, pady=0)

        self.ButtonNewLB.grid(row=1, column=25, sticky=tk.E, padx=0, pady=0)
        self.LBcbx_return.grid(row=1, column=27, sticky=tk.E, padx=0, pady=0)
        self.LBcbx_rus.grid(row=1, column=28, sticky=tk.E, padx=0, pady=0)
        self.lb_split_label.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
        self.LBcbx_SplitList.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
        self.LBent_SplitList.grid(row=1, column=30, sticky=tk.E, padx=0, pady=0)
        self.LBSpinSplitList.grid(row=1, column=31, sticky=tk.E, padx=0, pady=0)
        self.max_lb.grid(row=1, column=26, sticky=tk.E, rowspan=2, padx=0, pady=0)

        self.ButtonNewRB.grid(row=1, column=25, sticky=tk.E, padx=0, pady=0)
        self.RBcbx_return.grid(row=1, column=27, sticky=tk.E, padx=0, pady=0)
        self.RBcbx_rus.grid(row=1, column=28, sticky=tk.E, padx=0, pady=0)
        self.rb_split_label.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
        self.RBcbx_SplitList.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
        self.RBent_SplitList.grid(row=1, column=30, sticky=tk.E, padx=0, pady=0)
        self.RBSpinSplitList.grid(row=1, column=31, sticky=tk.E, padx=0, pady=0)
        self.max_rb.grid(row=1, column=26, sticky=tk.E, rowspan=2, padx=0, pady=0)

        self.t5l.grid(row=10, column=1, sticky=tk.E, padx=0, pady=0)
        self.t5r.grid(row=15, column=1, sticky=tk.E, padx=0, pady=0)

        self.LB.grid(row=11, column=0, sticky=tk.EW, padx=0, pady=0)
        self.LB.scrolly.grid(row=11, column=1, sticky=tk.NSEW, padx=0, pady=0)
        self.LB.scrollx.grid(row=12, column=0, sticky=tk.NSEW, padx=0, pady=0)
        self.LB.label_info.grid(row=10, column=0, sticky=tk.NSEW, padx=0, pady=0)

        self.RB.grid(row=16, column=0, sticky=tk.EW, padx=0, pady=0)
        self.RB.scrolly.grid(row=16, column=1, sticky=tk.NSEW, padx=0, pady=0)
        self.RB.scrollx.grid(row=17, column=0, sticky=tk.NSEW, padx=0, pady=0)
        self.RB.label_info.grid(row=15, column=0, sticky=tk.NSEW, padx=0, pady=0)

        self.spin_LB_height.grid(row=1, column=64, sticky=tk.E, padx=0, pady=0)
        self.ButtonLB_note.grid(row=1, column=65, sticky=tk.E, padx=0, pady=0)
        self.partNumEmptyLbNext.grid(row=1, column=56, sticky=tk.E, padx=0, pady=0)
        self.partNumDenyLbNext.grid(row=1, column=57, sticky=tk.E, padx=0, pady=0)

        self.LbB1Cbx.grid(row=1, column=54, sticky=tk.E, padx=0, pady=0)
        self.LbB2Cbx.grid(row=1, column=55, sticky=tk.E, padx=0, pady=0)
        self.LbRstripCbx.grid(row=1, column=61, sticky=tk.E, padx=0, pady=0)
        self.LbEndCbx.grid(row=1, column=62, sticky=tk.E, padx=0, pady=0)

        self.spin_RB_height.grid(row=1, column=64, sticky=tk.E, padx=0, pady=0)
        self.ButtonRB_note.grid(row=1, column=65, sticky=tk.E, padx=0, pady=0)
        self.partNumEmptyRbNext.grid(row=1, column=58, sticky=tk.E, padx=0, pady=0)
        self.partNumDenyRbNext.grid(row=1, column=59, sticky=tk.E, padx=0, pady=0)

        self.RbB1Cbx.grid(row=1, column=56, sticky=tk.E, padx=0, pady=0)
        self.RbB2Cbx.grid(row=1, column=57, sticky=tk.E, padx=0, pady=0)
        self.RbRstripCbx.grid(row=1, column=62, sticky=tk.E, padx=0, pady=0)
        self.RbEndCbx.grid(row=1, column=63, sticky=tk.E, padx=0, pady=0)

        self.ButtonParamFileOpen.grid(row=1, column=5, sticky=tk.EW, padx=0, pady=0)
        self.ButtonClearDown.grid(row=1, column=8, sticky=tk.E, padx=0, pady=0)
        self.ButtonClearUp.grid(row=1, column=15, sticky=tk.E, padx=0, pady=0)
        self.ButtonNote.grid(row=1, column=6, sticky=tk.EW, padx=0, pady=0)
        self.ButtonLog.grid(row=1, column=7, sticky=tk.E, padx=0, pady=0)
        self.cbxClipboard.grid(row=5, column=5, sticky=tk.E, padx=0, pady=0)
        self.cbxOrdVersion.grid(row=5, column=3, sticky=tk.N, padx=0, pady=0)
        self.cbxAutoNoteParam.grid(row=5, column=4, sticky=tk.E, padx=0, pady=0)
        self.cbxAutoShowParam.grid(row=1, column=20, sticky=tk.E, padx=0, pady=0)
        self.cbxClearShow.grid(row=5, column=6, sticky=tk.E, padx=0, pady=0)

        self.change_folder_cbx.grid(row=1, column=101, sticky=tk.E, padx=0, pady=0)
        self.deny_file_cbx.grid(row=1, column=102, sticky=tk.E, padx=0, pady=0)
        self.filesStats_cbx.grid(row=1, column=103, sticky=tk.E, padx=0, pady=0)

        self.LBent_SplitList.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.LBent_SplitList.bind("<KeyRelease-Return>", self.comboParts_change)
        self.max_lb.bind("<KeyRelease-Return>", self.comboParts_change)

        self.RBent_SplitList.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.RBent_SplitList.bind("<KeyRelease-Return>", self.comboParts_change)
        self.max_rb.bind("<KeyRelease-Return>", self.comboParts_change)

        self.comboFiles.bind("<<ComboboxSelected>>", self.comboFiles_change)
        self.comboParts.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.comboParam.bind("<KeyRelease-Return>", self.get_files)
        self.max_inf.bind("<<ComboboxSelected>>", self.get_files)
        self.min_inf.bind("<<ComboboxSelected>>", self.get_files)
        self.sortKey1.bind("<<ComboboxSelected>>", self.setSortKey1)
        self.sortKey2.bind("<<ComboboxSelected>>", self.setSortKey2)
        self.comboLogger.bind("<<ComboboxSelected>>", lambda *a: defaults.VarWindowLogger.set(self.comboLogger.get()))
        self.LB.tag_configure('right', justify='right')

        self.comboParam['values'] = self.param_hist_list
        self.comboFiles['values'] = [self.no_files_text]
        self.comboParts['values'] = [0]
        self.comboFiles.current(0)
        self.comboParts.current(0)
        self.comboParam.current(0)
        self.set_comboFiles_width()
        self.set_rclick_menu()
        self.set_menu()

        # ToolTip
        t1 = '(1) Поле ввода {param}\n\t# Window.comboParam'
        t6 = '(6) получить web_reg_save_param, с учетом (1)-(5)\n\t# Window.ButtonShowParam\n\t# defaults.VarWrspDict' \
             ' -> param.web_reg_save_param'
        t2 = '(2) найти файлы(3), содержащие {param}(1)\n\t# Window.ButtonFindParamFiles\n\t' \
             '# defaults.VarParam.set->Window.comboParam->defaults.AllFiles->(3):defaults.FilesWithParam'
        lr_wlib.createToolTip(self.t2, t2)
        lr_wlib.createToolTip(self.t0, lr_help.CODE)
        # lr_wlib.createToolTip(self.t5, 'Форматирование строк LB/RB(5)')
        lr_wlib.createToolTip(self.t6, t6)
        lr_wlib.createToolTip(self.comboParam, t1)
        lr_wlib.createToolTip(self.t1, t1)
        lr_wlib.createToolTip(self.ButtonFindParamFiles, t2)
        self._TT_text_comboFiles = '(3) - выбор файла из результатов поиска (2):defaults.FilesWithParam\n\t' \
                                   '# Window.comboFiles == defaults.FilesWithParam\n\t# defaults.VarFileName -> ' \
                                   'defaults.VarFile ->(4):defaults.VarFileText\n\t\t\t-> defaults.VarPartNum'
        lr_wlib.createToolTip(self.comboFiles, self._TT_text_comboFiles)
        lr_wlib.createToolTip(self.sortKey1, 'sortKey1\nпри выборе - Формирует sortKey2.\nНекоторые ключи формируются '
                                             'после поиска(2)\n\t# Window.sortKey1\n\t# defaults.VarFileSortKey1 -> '
                                             'defaults.VarFileSortKey2')
        lr_wlib.createToolTip(self.sortKey2, 'sortKey2\nпри выборе - Сортировка файлов(3) в соответствие с выбранными '
                                             'sortKey ключами,\nте ключами файла(всплывающая подсказка для файла в '
                                             'комбобоксе(3), после поиска(2)).\nНекоторые ключи требуют включения '
                                             'чекбокса Статистика файлов.\n\t# Window.sortKey2\n\t'
                                             '# defaults.VarFileSortKey2 -> defaults.VarParam.set')
        lr_wlib.createToolTip(self.t3, self._TT_text_comboFiles)
        t4 = '(4) - порядковый номер вхождения {param} в файл(3).\nparam(1) в файле может встречатся несколько раз,\n' \
             'с разными (5)LB/RB. Нумерация с 0.\n\t# Window.comboParts == file["Param"]["Count"]\n\t' \
             '# defaults.VarPartNum -> defaults.VarLB/defaults.VarRB'
        lr_wlib.createToolTip(self.comboParts, t4)
        lr_wlib.createToolTip(self.t4, t4)
        lr_wlib.createToolTip(self.t01, lr_help.WORK)
        lr_wlib.createToolTip(self.t02, lr_help.ADD)
        lr_wlib.createToolTip(self.cbxOrdVersion, 'версия функции поиска Ord: param.find_param_ord\n1 - новая(7.2.0)\n'
                                                  '0 - старая - не находит Ord при пересечении LB/RB\n\t'
                                                  '# Windows.cbxOrdVersion\n\t# defaults.VarOrdVersion')
        lr_wlib.createToolTip(self.spin_toolTipTimeout, 'время жизни, всплывающих подсказок, в мсек,\nтк подсказки '
                                                        'иногда намертво "зависают"\n 0 - "отключить" оборбражение\n\t'
                                                        '# Windows.spin_toolTipTimeout\n\t# defaults.VarToolTipTimeout')
        lr_wlib.createToolTip(self.t5l, '(5) LB - Левое поле.\nПри необходимости, необходимо отредактировать,\n'
                                        'если в поле попал "вариативный" параметр, нежелательные спец символы, и тд.\n'
                                        'После, нажать (6), для получения web_reg_save_param с новым Ord и LB\n'
                                        'УДАДЯТЬ символы из поля ТОЛЬКО "СЛЕВ"А{param} НАПРАВО,\nте Последний LB '
                                        'символ/ы удалять нельзя.\n\t# Window.LB\n\t# defaults.VarLB')
        lr_wlib.createToolTip(self.t5r, '(5) RB - Правое поле.\nПри необходимости, необходимо отредактировать,\n'
                                        'если в поле попал "вариативный" параметр, нежелательные спец символы, и тд.\n'
                                        'После, нажать (6), для получения web_reg_save_param с новым Ord и RB\nУДАДЯТЬ '
                                        'символы из поля ТОЛЬКО СПРАВА {param}Н"ЕЛЕВО",\nте Первый RB символ/ы удалять '
                                        'нельзя.\n\t# Window.RB\n\t# defaults.VarRB')
        lr_wlib.createToolTip(self.ButtonShowParam, t6)
        lr_wlib.createToolTip(self.ButtonNewLB, 'заново сформировать (5)LB, с учетом (1)-(5)\n\t# Window.ButtonNewLBRB '
                                                '-> defaults.VarPartNum')
        lr_wlib.createToolTip(self.ButtonNewRB, 'заново сформировать (5)RB, с учетом (1)-(5)\n\t# Window.ButtonNewLBRB '
                                                '-> defaults.VarPartNum')

        lr_wlib.createToolTip(self.LbB1Cbx, 'по LB определить, если param находится внутри фигурных скобок: '
                                            '{... value="zkau_1", ...}\nЕсди да, установить '
                                            'defaults.VarSplitListNumRB.set(1)\n\t# Window.LbB1Cbx\n\tdefaults.VarLbB1')
        lr_wlib.createToolTip(self.RbB1Cbx, 'по RB определить, если param находится внутри фигурных скобок: '
                                            '{... value="zkau_1", ...}\nЕсди да, установить '
                                            'defaults.VarSplitListNumRB.set(1)\n\t# Window.RbB1Cbx\n\tdefaults.VarRbB1')

        lr_wlib.createToolTip(self.LbB2Cbx, 'по LB определить, если param находится внутри квадратных скобок: '
                                            '[... value="zkau_1", ...]\nЕсди да, установить '
                                            'defaults.VarSplitListNumRB.set(3)\n\t# Window.LbB2Cbx\n\tdefaults.VarLbB2')
        lr_wlib.createToolTip(self.RbB2Cbx, 'по RB определить, если param находится внутри квадратных скобок: '
                                            '[... value="zkau_1", ...]\nЕсди да, установить '
                                            'defaults.VarSplitListNumRB.set(3)\n\t# Window.RbB2Cbx\n\tdefaults.VarRbB2')

        lr_wlib.createToolTip(self.RbRstripCbx, 'обрезать Rb справа, до string.whitespace символов\n\t'
                                                '# Window.RbRstripCbx\n\tdefaults.VarRbRstrip')
        lr_wlib.createToolTip(self.LbRstripCbx, 'обрезать Lb слева, до string.whitespace символов\n\t'
                                                '# Window.LbRstripCbx\n\tdefaults.VarLbRstrip')

        lr_wlib.createToolTip(self.RbEndCbx, 'обрезать Rb, справа, до нежелательных символов, например "[]{},"\n\t'
                                                '# Window.RbEndCbx\n\tdefaults.VarREnd')
        lr_wlib.createToolTip(self.LbEndCbx, 'обрезать Lb, слева, до нежелательных символов, например "[]{},"\n\t'
                                                '# Window.LbEndCbx\n\tdefaults.VarLEnd')

        lr_wlib.createToolTip(self.actionButton, 'открыть action.c файл, для поиска {param} из меню правой кнопки мыши'
                                                 '\n\t# Window.actionButton')
        lr_wlib.createToolTip(self.ButtonNote, 'tk.Text в Блокнот/Editor\n\t# Window.ButtonNote')
        lr_wlib.createToolTip(self.ButtonLog, 'лог в Блокнот/Editor\n\t# Window.ButtonLog')
        lr_wlib.createToolTip(self.max_lb, 'макс кол-во символов в LB(5)\nнажать Enter\n\t# Window.max_lb_rb\n\t'
                                           '# defaults.VarMaxLen')
        lr_wlib.createToolTip(self.max_rb, 'макс кол-во символов в RB(5)\nнажать Enter\n\t# Window.max_lb_rb\n\t'
                                           '# defaults.VarMaxLen')
        lr_wlib.createToolTip(self.Button_change_folder, 'Смена директории поиска {param} файлов\n\t'
                                                         '# Window.Button_change_folder\n\t# defaults.VarFilesFolder '
                                                         '-> defaults.AllFiles')
        lr_wlib.createToolTip(self.ButtonParamFileOpen, 'файл(3) в Блокнот/Editor\n\t# Window.ButtonParamFileOpen')
        lr_wlib.createToolTip(self.ButtonClearUp, 'очистить tk.Text\n\t# Window.ButtonClearUp')
        lr_wlib.createToolTip(self.ButtonClearDown, 'очистить все поля ввода\n\t# Window.ButtonClearDown')
        lr_wlib.createToolTip(self.cbxClearShow, 'очищать tk.Text,\nперед выводом(6)\n\t# Window.cbxClearShow')
        lr_wlib.createToolTip(self.LBcbx_SplitList, "обрезать LB(5) до ->>\n\t# Window.LBcbx_SplitList\n\t"
                                                    "# defaults.VarSplitListLB")
        lr_wlib.createToolTip(self.RBcbx_SplitList, "обрезать RB(5) до ->>\n\t# Window.RBcbx_SplitList\n\t"
                                                    "# defaults.VarSplitListRB")
        lr_wlib.createToolTip(self.LBent_SplitList, "<<- обрезать LB(5) до первого встретившегося значения из "
                                                    "eval([ '...', ... ])\nПри необходимости, можно добавить/удалить "
                                                    "строки-разделители\nДелить, Не учитывая последних N символов "
                                                    "строки LB(5) ->>\n\t# Window.ent_SplitList <- "
                                                    "Window.LBcbx_SplitList")
        lr_wlib.createToolTip(self.RBent_SplitList, "<<- обрезать RB(5) до первого встретившегося значения из "
                                                    "eval([ '...', ... ])\nПри необходимости, можно добавить/удалить "
                                                    "строки-разделители\nДелить, Не учитывая первых N символов строки "
                                                    "RB(5) ->>\n\t# Window.ent_SplitList <- Window.RBcbx_SplitList")
        lr_wlib.createToolTip(
            self.LBSpinSplitList,
            '<<- Не учитывать N последних символов LB, при SplitList обрезке\nСтратерия использования:\n'
            ' 1 - (не рекомендуется) для формирования короткого и "безопасного" LB=, как следствие очень большой Ord=\n'
            ' 2 - (безопасный вариант) для формирования более короткого, но более "безопасного" LB=, '
            'как следствие большой Ord=\n'
            ' 3 - (основной вариант) для формирования более длинного LB=, как следствие маленький Ord='
            '\n\t# Window.LBSpinSplitList\n\t# defaults.VarSplitListNumLB')
        lr_wlib.createToolTip(
            self.RBSpinSplitList,
            '<<- Не учитывать первых N символов RB, при SplitList обрезке\n'
            ' 1 - (безопасный вариант) если param находится внутри фигурных скобок: {... value="zkau_1", ...}\n'
            '  те не гарантируется, что справа от "zkau_1"," будут теже символы.\n'
            '  для формирования короткого и "безопасного" RB=, как следствие очень большой Ord=\n'
            ' 2 - (основной вариант) если неизвестно где находится param\n'
            '  для формирования более короткого, но более "безопасного" RB=, как следствие большой Ord=\n'
            ' 3 и больше - (доп вариант) если param находится внутри квадратных скобок: [... value="zkau_1", ...]\n'
            '   для формирования более длинного RB=, как следствие маленький Ord='
            '\n\t# Window.LBSpinSplitList\n\t# defaults.VarSplitListNumRB')
        lr_wlib.createToolTip(self.cbxClipboard, 'копировать web_reg_save_param в буфер обмена\nпри выводе(6)\n\t'
                                                 '# Window.cbxClipboard')
        lr_wlib.createToolTip(self.LBcbx_return, 'обрезать (5)LB до переноса строки\n\t# Window.cbx_return\n\t'
                                                 '# defaults.VarReturn -> defaults.VarPartNum')
        lr_wlib.createToolTip(self.RBcbx_return, 'обрезать (5)RB до переноса строки\n\t# Window.cbx_return\n\t'
                                                 '# defaults.VarReturn -> defaults.VarPartNum')
        lr_wlib.createToolTip(self.LBcbx_rus, 'обрезать (5)LB до не ASCII либо Русских символов\n\t# Window.cbx_rus\n\t'
                                              '# defaults.VarRus -> defaults.VarPartNum')
        lr_wlib.createToolTip(self.RBcbx_rus, 'обрезать (5)RB до не ASCII либо Русских символов\n\t# Window.cbx_rus\n\t'
                                              '# defaults.VarRus -> defaults.VarPartNum')
        lr_wlib.createToolTip(self.spin_RB_height, 'изменить высоту RB\n\t# Window.spin_RB_height')
        lr_wlib.createToolTip(self.ButtonRB_note, 'RB в Блокнот/Editor\n\t# Window.ButtonRB_note')
        lr_wlib.createToolTip(self.spin_LB_height, 'изменить высоту LB\n\t# Window.spin_LB_height')
        lr_wlib.createToolTip(self.change_folder_cbx, 'Определить Файлы, для поиска(2)\n On - Только файлы прописанные '
                                                      'в *.inf - формат LoadRunner\n Off - Все файлы каталога\n\t'
                                                      '# Window.change_folder_cbx\n\t# defaults.VarIsInfFiles -> '
                                                      'defaults.AllFiles')
        lr_wlib.createToolTip(self.ButtonLB_note, 'LB в Блокнот/Editor\n\t# Window.ButtonLB_note')
        lr_wlib.createToolTip(self.cbxPopupWindow, 'показывать popup окна\nфинальные результаты, ошибки и тд\n\t'
                                                   '# Window.cbxPopupWindow\n\t# defaults.VarShowPopupWindow')
        lr_wlib.createToolTip(self.min_inf, 'min номер inf.\nнижняя граница t*.inf, при поиске(2)\n\t# Window.min_inf'
                                            '\n\t# defaults.VarSearchMinInf -> defaults.VarParam.set')
        lr_wlib.createToolTip(self.max_inf, 'max номер inf.\nверхняя граница t*.inf, при поиске(2)\n\t# Window.max_inf'
                                            '\n\t# defaults.VarSearchMaxInf -> defaults.VarParam.set')
        lr_wlib.createToolTip(self.cbxAutoNoteParam, 'открыть web_reg_save_param в Блокнот/Editor,\nпри выводе(6)\n\t'
                                                     '# Window.cbxAutoNoteParam')
        lr_wlib.createToolTip(self.deny_file_cbx, 'Определить Файлы, для поиска(2)\n On - Все файлы.\n '
                                                  'Off - Исключить файлы, подходящие под "списк исключения"\n         '
                                                  'defaults.DENY_* : *.c, *.gif, *.zip, ..., "*_Request*" и тд.\n\t'
                                                  '# Window.deny_file_cbx\n\t# defaults.VarAllowDenyFiles -> '
                                                  'defaults.AllFiles')
        lr_wlib.createToolTip(self.cbxAutoShowParam, 'формировать web_reg_save_param, после поиска(2)\n те выполнять '
                                                     'шаги (3)-(6) автоматически\n\t# Window.cbxWrspAutoCreate')
        lr_wlib.createToolTip(
            self.StrongSearchInFile_cbx, 'принудительно использовать контроль LB/RB(на недопустимые символы), '
                                         '\nпри поиске(2) param(1), в файлах(3) ответов\n'
                                         'вкл - меньше (3) и (4), те только "корректные"\n'
                                         'выкл - любые доступные (3) и (4), с ним лучше отключать чекб strip и deny'
                                         '\n\t# Window.StrongSearchInFile_cbx\n\t# defaults.VarStrongSearchInFile')
        lr_wlib.createToolTip(self.filesStats_cbx, 'Статискика файлов\n On - создать ститистику Сразу, для всех файлов'
                                                   ' (размер, кол-во символов и тд)\n       замедляет старт, ускоряет '
                                                   'дальнейшую работу\n Off - создавать ститистику Отдельно, но '
                                                   'однократно, для каждого выбранного файла\n         чтение '
                                                   'статистики, однократно замедлит чтение любого выбранного файла\n '
                                                   '        при выкл, сортировка специфическими sortKey1/2, может '
                                                   'работать некорректно\n\t# Window.filesStats_cbx\n\t'
                                                   '# defaults.VarAllFilesStatistic -> defaults.AllFiles')
        lr_wlib.createToolTip(self.cbxFirstLastFile, 'выброр файла в (3)\non - последний\noff - первый\n\t'
                                                     '# Window.cbxFirstLastFile\n\t# defaults.VarFirstLastFile -> '
                                                     'defaults.VarFileName')
        lr_wlib.createToolTip(self.cbxFileNamesNumsShow, 'показывать имена найденых файлов и inf номера, после '
                                                         'поиска(2)\n\t# Window.cbxFileNamesNumsShow\n\t'
                                                         '# defaults.VarFileNamesNumsShow')
        lr_wlib.createToolTip(self.comboLogger, 'минимальный уровень вывода сообщений в gui\n\t# Window.comboLogger\n\t'
                                                '# defaults.VarWindowLogger')
        lr_wlib.createToolTip(self.unblock, 'разблокировать виджеты, во время работы\n\t# Window.unblock')
        lr_wlib.createToolTip(self.partNumEmptyLbNext, 'использовать следующее param вхождение(4) или файл(3)\n'
                                                       'при пустом str.strip(LB(5))\n\t# Window.partNumEmptyLbNext\n\t'
                                                       '# defaults.VarPartNumEmptyLbNext')
        lr_wlib.createToolTip(self.partNumEmptyRbNext, 'использовать следующее param вхождение(4) или файл(3)\n'
                                                       'при пустом str.strip(RB(5))\n\t# Window.partNumEmptyRbNext\n\t'
                                                       '# defaults.VarPartNumEmptyRbNext')
        lr_wlib.createToolTip(self.partNumDenyLbNext, 'использовать следующее param вхождение(4) или файл(3)\n'
                                                      'при недопустимом LB(5), если последний cимвол LB:\nБуква, Цифра,'
                                                      ' или "_!-"\n\t# Window.partNumDenyLbNext\n\t'
                                                      '# defaults.VarPartNumDenyLbNext')
        lr_wlib.createToolTip(self.partNumDenyRbNext, 'использовать следующее param вхождение(4) или файл(3)\nпри '
                                                      'недопустимом RB(5), если первый cимвол RB:\nБуква, Цифра, или '
                                                      '"_!-"\n\t# Window.partNumDenyRbNext\n\t'
                                                      '# defaults.VarPartNumDenyRbNext')
        # виджеты для блокирования
        self.configure_attrs = {
            a: getattr(self, a).configure for a in dir(self) if hasattr(getattr(self, a), 'configure')}

        defaults.Window.set_folder()
        if action and lr_action._action_file():
            lr_action.ActionWindow(auto_param_creator=auto_param_creator)

    def err_to_widgts(self, exc_type, exc_val, exc_tb, ern) -> None:
        '''отображение ошибки'''
        err = '{n}( {e} )'.format(n=ern, e=exc_val)
        defaults.Tk.title('{e} | {v}'.format(e=err, v=defaults.VERSION))
        self.last_frame.config(text='\n'.join(err.split('\n')[:5])[:500])
        # lr_wlib.createToolTip(self.comboFiles, '\n'.join(lr_other._chunks(str(exc_val), 60)))

    def set_menu(self) -> None:
        '''menubar'''
        def set_editor() -> None:
            '''Select Editor'''
            __file = tk.filedialog.askopenfile()
            if __file:
                defaults.EDITOR['exe'] = __file.name

        self.menubar = tk.Menu(defaults.Tk)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Select Encode", command=self.enc_wind)
        filemenu.add_command(label="Pools", command=self.pool_wind)
        filemenu.add_command(label="Select Editor", command=set_editor)
        filemenu.add_command(label="Select Folder", command=self.change_folder_ask)
        filemenu.add_command(label="AllFiles list", command=self.folder_wind)
        filemenu.add_command(label="LoadRunner action.c", command=lr_action.ActionWindow)
        filemenu.add_command(label="Help", command=lambda *a: lr_log.Logger.info(lr_help.CODE + '\n' + lr_help.HELP))
        filemenu.add_command(label="Exit", command=defaults.Tk.destroy)
        self.menubar.add_cascade(label="Menu", menu=filemenu)
        defaults.Tk.config(menu=self.menubar)

    def set_rclick_menu(self) -> None:
        '''меню правой кнопки мыши'''
        lr_wlib.rClickbinder(self)  # все tk
        for widj in dir(self):
            with contextlib.suppress(Exception):
                self.bind_class(getattr(self, widj), sequence='<Button-3>', func=lr_wlib.rClicker, add='')

    def folder_wind(self) -> None:
        '''окно списка всех файлов'''
        top = tk.Toplevel()
        top.transient(self)
        top.resizable(width=False, height=False)
        top.title('список всех файлов - %s' % len(defaults.AllFiles))
        comboAllFilesFolder = ttk.Combobox(top, foreground='grey', font=defaults.DefaultFont)
        buttonAllFilesFolder = tk.Button(
            top, text='open', font=defaults.DefaultFont + ' italic', padx=0, pady=0,
            command=lambda: subprocess.Popen([defaults.EDITOR['exe'], comboAllFilesFolder.get()]))
        ttip = lambda a: lr_wlib.createToolTip(comboAllFilesFolder, lr_other.file_string(lr_files.get_file_with_kwargs(
            defaults.AllFiles, FullName=comboAllFilesFolder.get()), deny=[]))
        comboAllFilesFolder.bind("<<ComboboxSelected>>", ttip)
        lr_wlib.createToolTip(buttonAllFilesFolder, 'открыть выбранный файл')
        lr_wlib.createToolTip(comboAllFilesFolder, 'список всех файлов, в которых производится поиск {param}'
                                                   '\n\t# Window.folder_wind\n\t# defaults.AllFiles')
        files = list(f['File']['FullName'] for f in defaults.AllFiles)
        comboAllFilesFolder['values'] = files
        with contextlib.suppress(Exception):
            m = max(len(f) for f in files)
            if m > 100: m = 100
            comboAllFilesFolder.configure(width=m)
        buttonAllFilesFolder.pack()
        comboAllFilesFolder.pack()

    def enc_wind(self) -> None:
        '''окно кодировки файлов'''
        top = tk.Toplevel()
        top.transient(self)
        top.resizable(width=False, height=False)
        tt = 'кодировка файлов для (2)-(5)\n\t# Window.enc_wind'
        top.title(tt)
        encodeEntry = ttk.Combobox(
            top, justify='center', textvariable=defaults.VarEncode, width=65, foreground='grey',
            background=defaults.Background, font=defaults.DefaultFont + ' italic')
        encodeEntry['values'] = defaults.ENCODE_LIST
        encodeEntry.bind("<<ComboboxSelected>>", lambda *a: self.comboFiles_change())
        lr_wlib.createToolTip(encodeEntry, tt)
        encodeEntry.pack()

    def pool_wind(self) -> None:
        '''окно настройки пулов'''
        top = tk.Toplevel()
        top.transient(self)
        top.resizable(width=False, height=False)
        tt = 'окно настройки пулов  # Window.pool_wind'
        top.title(tt)

        def set_pool(pool: lr_pool.POOL) -> None:
            '''установить новый пул'''
            pool.reset()
            self.last_frame_text_set()

        labMP = tk.Label(top, text='MPPool')
        labMP.grid(row=1, column=1)
        lr_wlib.createToolTip(labMP, 'основной пул(process), поиск в файлах и тд')

        entryMPName = ttk.Combobox(
            top, justify='center', textvariable=lr_pool.M_POOL.name, width=65, foreground='grey',
            background=defaults.Background, font=defaults.DefaultFont + ' italic')
        entryMPName['values'] = list(lr_pool.POOL.pools.keys())
        entryMPName.bind("<<ComboboxSelected>>", lambda *a: set_pool(lr_pool.M_POOL))
        lr_wlib.createToolTip(entryMPName, 'тип MP пула(любые стандартные(process))')
        entryMPName.grid(row=2, column=0, columnspan=7)

        spinMP = tk.Spinbox(
            top, from_=0, to=999, textvariable=lr_pool.M_POOL.size, width=3,
            font=defaults.DefaultFont, command=lambda *a: set_pool(lr_pool.M_POOL))
        spinMP.grid(row=2, column=7)
        lr_wlib.createToolTip(spinMP, 'размер MP пула')

        labT = tk.Label(top, text='TPool')
        labT.grid(row=3, column=1)
        lr_wlib.createToolTip(labT, 'доп пул(thread only), выполнение в фоне, подсветка и тд')

        entryTName = ttk.Combobox(
            top, justify='center', textvariable=lr_pool.T_POOL.name, width=65, foreground='grey',
            background=defaults.Background, font=defaults.DefaultFont + ' italic')
        entryTName['values'] = list(lr_pool.POOL.pools.keys())
        entryTName.bind("<<ComboboxSelected>>", lambda *a: set_pool(lr_pool.T_POOL))
        lr_wlib.createToolTip(entryTName, 'тип T пула(чтото из thread)')
        entryTName.grid(row=4, column=0, columnspan=7)

        spinT = tk.Spinbox(
            top, from_=0, to=999, textvariable=lr_pool.T_POOL.size, width=3,
            font=defaults.DefaultFont, command=set_pool(lr_pool.T_POOL))
        spinT.grid(row=4, column=7)
        lr_wlib.createToolTip(spinT, 'размер T пула')

        spinSThreadAutoSizeTimeOut = tk.Spinbox(
            top, from_=0, to=10**5, textvariable=defaults.SThreadAutoSizeTimeOut, width=4, font=defaults.DefaultFont)
        spinSThreadAutoSizeTimeOut.grid(row=5, column=2)
        lr_wlib.createToolTip(spinSThreadAutoSizeTimeOut, 'SThreadAutoSizeTimeOut отзывчивость(мсек) SThreadPool - '
                                                          'период опроса, для изменения размера пула')

        spinMainThreadUpdateTime = tk.Spinbox(
            top, from_=0, to=10**5, textvariable=defaults.MainThreadUpdateTime, width=4, font=defaults.DefaultFont)
        spinMainThreadUpdateTime.grid(row=5, column=0)
        lr_wlib.createToolTip(spinMainThreadUpdateTime, 'MainThreadUpdateTime интервал(мс) проверки очереди выполнения '
                                                        'для главного потока')

        spinSThreadPoolSizeMin = tk.Spinbox(
            top, from_=0, to=10 ** 5, textvariable=defaults.SThreadPoolSizeMin, width=4, font=defaults.DefaultFont)
        spinSThreadPoolSizeMin.grid(row=5, column=3)
        lr_wlib.createToolTip(spinSThreadPoolSizeMin, 'SThreadPool min size')

        spinSThreadPoolSizeMax = tk.Spinbox(
            top, from_=0, to=10 ** 5, textvariable=defaults.SThreadPoolSizeMax, width=4, font=defaults.DefaultFont)
        spinSThreadPoolSizeMax.grid(row=5, column=4)
        lr_wlib.createToolTip(spinSThreadPoolSizeMax, 'SThreadPool max size (int>2)')

        spinSThreadPoolAddMinQSize = tk.Spinbox(
            top, from_=0, to=10 ** 5, textvariable=defaults.SThreadPoolAddMinQSize, width=4, font=defaults.DefaultFont)
        spinSThreadPoolAddMinQSize.grid(row=5, column=5)
        lr_wlib.createToolTip(spinSThreadPoolAddMinQSize, 'SThreadPool - минимальная длина очереди, для добавления, '
                                                          'более чем одного потока, за раз')

        spinSThreadPooMaxAddThread = tk.Spinbox(
            top, from_=0, to=10 ** 5, textvariable=defaults.SThreadPooMaxAddThread, width=4, font=defaults.DefaultFont)
        spinSThreadPooMaxAddThread.grid(row=5, column=6)
        lr_wlib.createToolTip(spinSThreadPooMaxAddThread, 'SThreadPool - max число потоков, для добавления '
                                                          'за один раз(до SThreadPoolSizeMax)')

        spinSThreadExitTimeout = tk.Spinbox(
            top, from_=0, to=10 ** 5, textvariable=defaults.SThreadExitTimeout, width=4, font=defaults.DefaultFont)
        spinSThreadExitTimeout.grid(row=5, column=1)
        lr_wlib.createToolTip(spinSThreadExitTimeout, 'SThreadPool таймаут(сек) выхода, бездействующих потоков'
                                                      '(до SThreadPoolSizeMin)')
        spinSThreadMonitorUpdate = tk.Spinbox(
            top, from_=0, to=10 ** 5, textvariable=defaults._SThreadMonitorUpdate, width=4, font=defaults.DefaultFont)
        spinSThreadMonitorUpdate.grid(row=5, column=7)
        lr_wlib.createToolTip(spinSThreadMonitorUpdate, 'SThreadPool (мс) время обновления Window.pool_wind текста состояния пула')

        if defaults.T_POOL_NAME == 'SThreadPool(threading.Thread)':
            self.pool_state_updater()

    @lr_pool.T_POOL_execute_decotator
    def pool_state_updater(self) -> None:
        '''SThreadPool(threading.Thread) текст состояния пула'''
        def pool_state_string(st=lambda i: '{0:<6} : {1}'.format(*i)) -> str:
            '''инфо о потоках T_POOL'''
            s = '\n'.join('\n{n} {t}'.format(t=('\n' + '\n'.join(map(st, t.task.items())) if t.task else 'sleep'),
                                             n=t.name) for t in lr_pool.T_POOL.threads)
            return s

        def thread_info_updater(y: lr_wlib.YesNoCancel) -> None:
            '''перезапуск инфо'''
            t1, t2 = y.label1['text'].split('\n', 1)
            t1 = '{0}: size({1})'.format(t1.split(':', 1)[0], len(lr_pool.T_POOL.threads))
            y.label1.config(text='{0}\n{1}'.format(t1, t2))
            y.new_text(pool_state_string())
            if y.alive_:
                y.after(defaults._SThreadMonitorUpdate.get(), thread_info_updater, y)

        y = lr_wlib.YesNoCancel(
            ['выйти'], 'монитор T_POOL\n{}[ {} ] : {}'.format(lr_pool.SThreadPool, lr_pool.SThread, lr_pool.auto_size_SThreadPool),
            'инфо о задачах, выполняющихся в SThread потоках', title=self.pool_state_updater, parent=self, is_text=pool_state_string())
        y.after(50, thread_info_updater, y)
        y.ask()

    def auto_update_action_pool_lab(self) -> None:
        '''обновление action.label с процентами и пулом'''
        if self.action_windows:
            for act in self.action_windows.values():
                if hasattr(lr_pool.T_POOL.pool, 'queue_in'):
                    pt = 'T:q_in\n{t} : {q_in}'.format(t=lr_pool.T_POOL._size, q_in=lr_pool.T_POOL.pool.queue_in.qsize())
                else:
                    pt = '  T\n  {t}'.format(t=lr_pool.T_POOL._size)

                if hasattr(lr_pool.M_POOL.pool, 'queue_in'):
                    pm = 'M:q_in\n{mp} : {q_in}'.format(mp=lr_pool.M_POOL._size, q_in=lr_pool.M_POOL.pool.queue_in.qsize())
                else:
                    pm = '  M {mp}'.format(mp=lr_pool.M_POOL._size)

                act.scroll_lab2.config(text='{p:>3}%\n\npool:\n\n{pt}\n\n{pm}'.format(
                    p=round(int(act.tk_text.linenumbers.linenum) / (act.tk_text.highlight_lines._max_line / 100)),
                    pt=pt, pm=pm))

    def change_folder_ask(self, *args) -> None:
        '''смена директории поиска файлов'''
        d = tk.filedialog.askdirectory()
        if d:
            defaults.VarFilesFolder.set(d)
            with self.block():
                lr_files.createAllFiles()
            self.clear()

    def clear(self) -> None:
        '''очистить поля ввода'''
        self.show_frame_info_working()
        defaults.clearVars()
        self.LB.set('')
        self.RB.set('')
        self.comboFiles['values'] = [self.no_files_text]
        self.comboParts['values'] = [0]
        self.comboFiles.current(0)
        self.comboParts.current(0)
        lr_widj.LBRBText.set_label_text()
        self.set_comboFiles_width()
        self.sortKey1.set('Inf')
        self.sortKey2.set('Nums')
        self.last_frame_text_set()
        lr_wlib.createToolTip(self.comboFiles, self._TT_text_comboFiles)
        defaults.Tk.title(defaults.VERSION)

    def last_frame_text_set(self) -> None:
        self.last_frame['text'] = 'inf={i}: файлов={f} | MP: {pool}[{p_size}] | T: {tpool}[{tpool_size}] | {d}'.format(
            d=defaults.VarFilesFolder.get(), f=len(defaults.AllFiles), pool=lr_pool.M_POOL._name,
            i=len(list(lr_other.get_files_infs(defaults.AllFiles))), tpool_size=lr_pool.T_POOL._size,
            p_size=lr_pool.M_POOL._size, tpool=lr_pool.T_POOL._name)

    def clear_before_find_param_files(self) -> None:
        '''очистка виджетов перед поиском'''
        self.LB.set('')
        self.RB.set('')
        lr_widj.LBRBText.set_label_text()
        self.comboFiles['values'] = [self.no_files_text]
        self.comboParts['values'] = [-1]
        self.comboFiles.current(0)
        self.comboParts.current(0)
        defaults.VarLB.set('')
        defaults.VarRB.set('')

    def clip_add(self, text: str) -> None:
        '''буфер обмена'''
        self.clipboard_clear()
        self.clipboard_append(text)

    def add_message(self, levelname: str, text: str) -> None:
        '''сообщения в конец текста gui'''
        with contextlib.suppress(Exception):
            if defaults.loggingLevels[defaults.VarWindowLogger.get()] <= defaults.loggingLevels[levelname]:
                self.tk_text.insert(tk.END, '{}\n'.format(text))
                self.tk_text.see(tk.END)

    def print(self, levelname: str, text: str) -> None:
        '''сообщения в конец текста gui, в main потоке'''
        lr_pool.MainThreadUpdater.submit(lambda: self.add_message(levelname, text))

    def set_comboFiles_width(self) -> None:
        '''установка макс ширины комбо файлов(3)'''
        l = max(len(f) for f in self.comboFiles['values'])
        m = defaults.VarMaxComboFilesWidth.get()
        self.comboFiles.configure(width=l if l < m else m)

    def setSortKey1(self, *args):
        '''комбо сортировки'''
        defaults.VarFileSortKey1.set(self.sortKey1.get())
        self.sortKey2['values'] = list(set(k for f in itertools.chain(defaults.AllFiles, defaults.FilesWithParam)
                                           for k in f.get(self.sortKey1.get(), ())))

    def setSortKey2(self, *args):
        '''комбо сортировки файлов(3)'''
        defaults.VarFileSortKey2.set(self.sortKey2.get())
        self.get_files()  # сортировка при поиске

    def show_frame_info_file(self) -> None:
        '''отображение всякой информации'''
        dt = defaults.VarWrspDict.get()
        defaults.Tk.title('"{param_Name}", {Name}, {inf_nums} > Файлы(из {files_all} найдено '
                          '{file_index}/{param_files}) | Вхождения({param_part}/{param_count}, всего {param_all} в '
                          '{_param_inf_all} inf) | {ver}'.format(ver=defaults.VERSION, **dt))
        self.main_frame['text'] = 'Inf{inf_nums}, Файл[{file_index}/{param_files}], ' \
                                  'Часть[{param_part}/{param_count}], {len} символов.'.format(**dt)

    def show_frame_info_working(self) -> None:
        '''отображение всякой информации'''
        self.main_frame['text'] = '{} | {} | ParamClipBoardSearchHotKey[{}]'.format(
            defaults.VarEncode.get(), time.strftime('%H:%M:%S'), defaults.FIND_PARAM_HOTKEY)
        self.last_frame['text'] = 'working ... %s' % defaults.VarFilesFolder.get()

    def set_maxmin_inf(self, files):
        '''установка виджетов min_inf max_inf'''
        infs = list(lr_other.get_files_infs(files))
        self.max_inf['values'] = list(reversed(infs))
        self.min_inf['values'] = infs
        self.max_inf.set(max(infs or [-1]))
        self.min_inf.set(min(infs or [-1]))

    def comboFiles_change(self, *args) -> None:
        '''при смене комбо(3), читать файл, записать комбо(4), выбрать файл по умолчанию (3)'''
        name = self.comboFiles.get()
        defaults.VarFileName.set(name)
        part = defaults.VarPartNum.get()
        self.comboPartsFill()
        self.comboParts.set(part if part else 0)
        self.comboParts_change()
        lr_wlib.createToolTip(self.comboFiles, lr_other.file_string(lr_files.get_file_with_kwargs(
            defaults.FilesWithParam, Name=name)))

    def comboPartsFill(self) -> None:
        '''заполнить комбобокс (4)'''
        file = defaults.VarFile.get()
        if defaults.VarStrongSearchInFile.get():
            self.comboParts['values'] = file['Param']['Count_indexs']
        else:
            self.comboParts['values'] = list(range(file['Param']['Count']))
        lr_wlib.createToolTip(defaults.Window.comboFiles, lr_other.file_string(lr_files.get_file_with_kwargs(
            defaults.FilesWithParam, Name=file['File']['Name'])))

    def comboParts_change(self, *args) -> None:
        '''смена комбо(4)'''
        defaults.VarPartNum.set(int(self.comboParts.get()))
        lr_widj.LBRBText.set_LB_RB()
        self.show_frame_info_file()

    def firstOrLastFile(self, *args) -> None:
        '''выбрать первый/последный файл в (3)'''
        i = (len(self.comboFiles['values']) - 1) if defaults.VarFirstLastFile.get() else 0
        self.comboFiles.current(i)
        self.comboFiles_change()

    def show_LR_Param(self, callback=None) -> str:
        '''показать web_reg_save_param (6)'''
        defaults.VarLB.set(self.LB.get())
        defaults.VarRB.set(self.RB.get())
        # с учетом редактирования LB/RB(5)
        web_reg_save_param = lr_param.create_web_reg_save_param(lr_param.wrsp_dict_creator())

        if web_reg_save_param:
            if self.cbxNotepadWrsp.get():
                lr_log.openTextInEditor(web_reg_save_param)
            if self.cbxWrspClipboard.get():
                self.clip_add(web_reg_save_param)
            if self.cbxClearShowVar.get():
                self.tk_text.delete(1.0, 'end')
            lr_log.Logger.info('{s}\n{wrsp}\n{s}'.format(s=defaults.PRINT_SEPARATOR, wrsp=web_reg_save_param))
            if callback:  # highlight
                callback()
        return web_reg_save_param

    def get_files(self, *args, param=None, clipb=False, callback=None, action=None) -> None:
        '''получить файлы с {param} (2)'''
        if param is not None:
            self.comboParam.set(param)
        self.show_frame_info_working()
        self.clear_before_find_param_files()
        param = self.comboParam.get()
        self.param_hist_list.insert(0, param)
        self.comboParam['values'] = self.param_hist_list

        with self.block():
            defaults.VarParam.set(param, set_file=False, action=action)  # получить файлы с {param}

        self.comboFiles['values'] = [f['File']['Name'] for f in defaults.FilesWithParam] or [self.no_files_text]
        self.set_comboFiles_width()
        self.firstOrLastFile()

        if clipb or self.cbxWrspClipboard.get():
            self.clip_add(self.show_LR_Param(callback))
        elif self.cbxWrspAutoCreate.get():
            self.show_LR_Param(callback)

        if defaults.FilesWithParam:
            self.sortKey1['values'] = sorted(set(k for f in defaults.FilesWithParam for k in f))

        self.last_frame['text'] = 'Файлы({files_all}->{param_files}) | ' \
                                  'INF(все[{all_inf_min}:{all_inf_max}]={all_inf_len}->' \
                                  'поиск[{param_inf_min}:{param_inf_max}]={search_inf_len}->' \
                                  'найдено[{_param_inf_min}:{_param_inf_max}]={_param_inf_all}) | ' \
                                  'Найдено {param_all} param.'.format(**defaults.VarWrspDict.get())

    def set_folder(self, callback=None) -> None:
        '''установка folder'''
        self.clear()
        with self.block():
            lr_files.createAllFiles()

        self.set_maxmin_inf(defaults.AllFiles)
        if defaults.AllFiles:
            self.sortKey1['values'] = sorted(set(k for f in defaults.AllFiles for k in f))

        self.last_frame_text_set()
        self.setSortKey1()
        if callback:
            callback()

    def on_closing(self) -> None:
        '''не выходить, при открытых action.c окнах'''
        if not self.action_windows or tk.messagebox.askokcancel(
                'выход', "Есть открытые action.c окна\n{a}\n все равно выйти?".format(
                    a=', '.join(map(str, self.action_windows)))):
            self.destroy()
            defaults.Tk.destroy()

    @contextlib.contextmanager
    def block(self, w=('text', 'tk_text', 'min_inf', 'max_inf', 'unblock', 'cbxPopupWindow', 'last_frame', )) -> iter:
        '''заблокировать/разблокировать виджеты в gui'''
        try:
            if self._block_:
                yield
            else:
                yield self._block(True, w=w)
        finally:
            if not self._block_:
                self._block(False, w=w)

    def _block(self, bl: bool, w=()) -> None:
        '''заблокировать/разблокировать виджеты в gui'''
        state = 'disabled' if bl else 'normal'
        attrs = self.configure_attrs
        for a in attrs:
            if a not in w:
                with contextlib.suppress(Exception):
                    attrs[a](state=state)
        with contextlib.suppress(Exception):
            self.update()
