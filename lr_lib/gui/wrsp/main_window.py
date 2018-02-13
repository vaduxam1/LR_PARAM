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

from tkinter import filedialog

import lr_lib.gui.widj.highlight_text
import lr_lib.gui.widj.lbrb5
import lr_lib.gui.etc.sub_menu
import lr_lib.gui.wrsp.top_wind
import lr_lib.gui.wrsp.tooltips
import lr_lib.gui.wrsp.grid

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.files as lr_files
import lr_lib.core.wrsp.param as lr_param
import lr_lib.core.etc.other as lr_other
import lr_lib.gui.action.main_action as lr_action
import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.etc.help as lr_help


class Window(ttk.Frame):
    cbxClearShowVar = tk.IntVar(value=lr_vars.cbxClearShowVar)  # перед (2), очищать центральный виджет текста
    cbxWrspClipboard = tk.IntVar(value=lr_vars.cbxWrspClipboard)  # после (2), копировать web_reg_save_param в буфер обмена
    cbxWrspAutoCreate = tk.IntVar(value=lr_vars.cbxWrspAutoCreate)  # после (2), выполнять (3)-(6)
    cbxNotepadWrsp = tk.IntVar(value=lr_vars.cbxNotepadWrsp)  # после (2), открывать web_reg_save_param в блокноте

    def __init__(self):
        self._block_ = None  # принудительно блокировать виджеты

        super().__init__(lr_vars.Tk, padding="0 0 0 0")
        lr_vars.Tk.protocol("WM_DELETE_WINDOW", self.on_closing)
        lr_vars.Tk.geometry('{}x{}'.format(*lr_vars._Tk_WIND_SIZE))
        lr_vars.Tk.option_add("*Listbox*Background", lr_vars.Background)
        # "масштабирование" виджетов окна
        lr_vars.Tk.grid_rowconfigure(0, weight=1)
        lr_vars.Tk.grid_columnconfigure(0, weight=1)
        lr_vars.Tk.title(lr_vars.VERSION)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=tk.NSEW)

        self.action_windows = collections.OrderedDict()  # спросить, перед выходом, если открыты action.c окна

        self.no_param_text = ''
        self.no_files_text = ''
        self.param_hist_list = [self.no_param_text]

        # создать виджеты
        self.main_frame = tk.LabelFrame(self, bd=2, labelanchor=tk.N, relief='groove', padx=0, pady=0, font=lr_vars.DefaultFont)
        self.mid_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.find_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.show_param_frame = ttk.Frame(self.main_frame, padding="0 0 0 0")
        self.last_frame = tk.LabelFrame(self, labelanchor=tk.S, bd=1, relief='groove', padx=0, pady=0, font=lr_vars.DefaultFont)

        self.sortKey1 = ttk.Combobox(self.last_frame, textvariable=lr_vars.VarFileSortKey1, justify='center',
                                     font=lr_vars.DefaultFont + ' italic', style="BW.TButton", width=10)
        self.sortKey2 = ttk.Combobox(self.last_frame, textvariable=lr_vars.VarFileSortKey2, justify='center',
                                     font=lr_vars.DefaultFont + ' italic', style="BW.TButton")

        # text
        self.tk_text = lr_lib.gui.widj.highlight_text.HighlightText(
            self, foreground='grey', background=lr_vars.Background, wrap=tk.NONE, height=10, padx=0, pady=0, undo=True, )
        self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
        self.tk_text.configure(yscrollcommand=self.text_scrolly.set, xscrollcommand=self.text_scrollx.set, bd=0, padx=0, pady=0)

        # (1)
        self.t1 = tk.Label(self.find_frame, text='(1)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.t0 = tk.Label(self.find_frame, text='?', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0, foreground='grey')
        self.t01 = tk.Label(self.show_param_frame, text='?', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0, foreground='grey')
        self.t02 = tk.Label(self.mid_frame, text='?', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0, foreground='grey')
        self.comboParam = ttk.Combobox(self.find_frame, textvariable=lr_vars.VarParam, justify='center', font=lr_vars.DefaultFont, width=54)
        self.cbxFirstLastFile = tk.Checkbutton(self.mid_frame, variable=lr_vars.VarFirstLastFile, text='last',
                                               font=lr_vars.DefaultFont + ' italic', padx=0, pady=0, command=self.firstOrLastFile)
        self.StrongSearchInFile_cbx = tk.Checkbutton(self.mid_frame, variable=lr_vars.VarStrongSearchInFile, padx=0, pady=0,
                                                     text='strong', font=lr_vars.DefaultFont + ' italic')

        self.actionButton = tk.Button(self.find_frame, text=' action.c  editor ', font=lr_vars.DefaultFont + ' italic bold',
                                      padx=0, pady=0, command=lr_action.ActionWindow, relief='ridge', background='orange')

        # (2)
        self.t2 = tk.Label(self.show_param_frame, text='(2)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.ButtonFindParamFiles = tk.Button(self.show_param_frame, text='поиск {param} в файлах ответов',
                                              font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0,
                                              command=lambda *a: lr_vars.Tk.after(0, self.get_files), background='orange')
        self.max_inf = ttk.Combobox(self.show_param_frame, width=10, textvariable=lr_vars.VarSearchMaxSnapshot,
                                    justify='center', foreground='grey', font=lr_vars.DefaultFont, style="BW.TButton")

        self.min_inf = ttk.Combobox(self.show_param_frame, width=10, textvariable=lr_vars.VarSearchMinSnapshot,
                                    justify='center', foreground='grey', font=lr_vars.DefaultFont, style="BW.TButton")

        # (3)
        self.t3 = tk.Label(self.mid_frame, text='(3)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.comboFiles = ttk.Combobox(self.mid_frame, state="readonly", justify='center', font=lr_vars.DefaultFont)

        # (4)
        self.t4 = tk.Label(self.mid_frame, text='(4)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.comboParts = ttk.Combobox(self.mid_frame, justify='center', width=5, font=lr_vars.DefaultFont + ' bold')

        # (5) LB/RB
        self.LB = lr_lib.gui.widj.lbrb5.LBRBText('LB', self)
        self.RB = lr_lib.gui.widj.lbrb5.LBRBText('RB', self)
        self.last_frameCbx1 = ttk.Label(self.LB.label_info, padding="0 0 0 0")
        self.last_frameCbx2 = ttk.Label(self.RB.label_info, padding="0 0 0 0")

        @lr_vars.T_POOL_decorator
        def lr_note(ob) -> None:
            lr_other.openTextInEditor(ob.get())

        self.t5l = tk.Label(self, text='(5)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.t5r = tk.Label(self, text='(5)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')

        SplitList = (lr_vars.SplitList, lr_vars._SplitList0, lr_vars._SplitList1, lr_vars._SplitList2, lr_vars._SplitList_3,
                     list(string.whitespace), 'list(string.ascii_letters)', 'list(string.digits)', 'list(string.punctuation)', )
        SplitList = tuple(str(l) for l in SplitList)

        # ---LB
        self.ButtonNewLB = tk.Button(self.last_frameCbx1, text='->', command=self.comboParts_change,
                                     font=lr_vars.DefaultFont + ' italic', width=2, padx=0, pady=0)
        self.LBcbx_return = tk.Checkbutton(self.last_frameCbx1, variable=lr_vars.VarReturnLB, text='\\n',
                                           font=lr_vars.DefaultFont + ' italic', command=self.comboParts_change, padx=0, pady=0, anchor=tk.S)
        self.LBcbx_rus = tk.Checkbutton(self.last_frameCbx1, variable=lr_vars.VarRusLB, text='ascii',
                                        font=lr_vars.DefaultFont + ' italic', command=self.comboParts_change, padx=0, pady=0)

        self.lb_split_label = tk.LabelFrame(self.last_frameCbx1, bd=1, padx=0, pady=0, relief='ridge')

        self.LBcbx_SplitList = tk.Checkbutton(self.lb_split_label, variable=lr_vars.VarSplitListLB, text='eval',
                                              font=lr_vars.DefaultFont + ' bold', command=self.spl_cbx_cmd_lb, padx=0, pady=0)
        self.LBent_SplitList = ttk.Combobox(self.lb_split_label, font=lr_vars.DefaultFont, width=10)
        self.LBent_SplitList['values'] = list(SplitList)
        self.LBent_SplitList.current(0)
        self.LBSpinSplitList = tk.Spinbox(self.lb_split_label, from_=0, to=100, textvariable=lr_vars.VarSplitListNumLB, width=2,
                                          font=lr_vars.DefaultFont, command=self.comboParts_change)

        self.max_lb = tk.Entry(self.last_frameCbx1, width=5, textvariable=lr_vars.VarMaxLenLB, justify='center',
                               foreground='grey', background=lr_vars.Background, font=lr_vars.DefaultFont + ' italic')
        self.spin_LB_height = tk.Spinbox(self.last_frameCbx1, from_=1, to=99, textvariable=self.LB.heightVar, width=2,
                                         command=self.LB.set_height, font=lr_vars.DefaultFont + ' italic', background=lr_vars.Background)
        self.ButtonLB_note = tk.Button(self.last_frameCbx1, text='edit', command=lambda: lr_note(self.LB), width=3,
                                       font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.partNumEmptyLbNext = tk.Checkbutton(self.last_frameCbx1, variable=lr_vars.VarPartNumEmptyLbNext, text='strip',
                                                 font=lr_vars.DefaultFont + ' bold', padx=0, pady=0)
        self.partNumDenyLbNext = tk.Checkbutton(self.last_frameCbx1, variable=lr_vars.VarPartNumDenyLbNext, text='deny',
                                                font=lr_vars.DefaultFont + ' bold', padx=0, pady=0)

        self.LbB1Cbx = tk.Checkbutton(self.lb_split_label, variable=lr_vars.VarLbB1, text='{', font=lr_vars.DefaultFont, padx=0, pady=0)
        self.LbB2Cbx = tk.Checkbutton(self.lb_split_label, variable=lr_vars.VarLbB2, text='[', font=lr_vars.DefaultFont, padx=0, pady=0)
        self.LbRstripCbx = tk.Checkbutton(self.last_frameCbx1, variable=lr_vars.VarLbLstrip, text='lstrip', font=lr_vars.DefaultFont, padx=0, pady=0)
        self.LbEndCbx = tk.Checkbutton(self.last_frameCbx1, variable=lr_vars.VarLEnd, text='end', font=lr_vars.DefaultFont, padx=0, pady=0)

        # ---RB
        self.ButtonNewRB = tk.Button(self.last_frameCbx2, text='->', command=self.comboParts_change,
                                     font=lr_vars.DefaultFont + ' italic', width=2, padx=0, pady=0)
        self.RBcbx_return = tk.Checkbutton(self.last_frameCbx2, variable=lr_vars.VarReturnRB, text='\\n', font=lr_vars.DefaultFont + ' italic',
                                           command=self.comboParts_change, padx=0, pady=0)
        self.RBcbx_rus = tk.Checkbutton(self.last_frameCbx2, variable=lr_vars.VarRusRB, text='ascii', font=lr_vars.DefaultFont + ' italic',
                                        command=self.comboParts_change, padx=0, pady=0)

        self.rb_split_label = tk.LabelFrame(self.last_frameCbx2, bd=1, padx=0, pady=0, relief='ridge')

        self.RBcbx_SplitList = tk.Checkbutton(self.rb_split_label, variable=lr_vars.VarSplitListRB, text='eval',
                                              font=lr_vars.DefaultFont + ' bold', command=self.spl_cbx_cmd_rb, padx=0, pady=0)
        self.RBent_SplitList = ttk.Combobox(self.rb_split_label, font=lr_vars.DefaultFont, width=10)
        self.RBent_SplitList['values'] = list(SplitList)
        self.RBent_SplitList.current(0)
        self.RBSpinSplitList = tk.Spinbox(self.rb_split_label, from_=0, to=100, textvariable=lr_vars.VarSplitListNumRB,
                                          width=2, font=lr_vars.DefaultFont, command=self.comboParts_change)

        self.max_rb = tk.Entry(self.last_frameCbx2, width=5, textvariable=lr_vars.VarMaxLenRB, justify='center', foreground='grey',
                               background=lr_vars.Background, font=lr_vars.DefaultFont + ' italic')
        self.partNumEmptyRbNext = tk.Checkbutton(self.last_frameCbx2, variable=lr_vars.VarPartNumEmptyRbNext, text='strip',
                                                 font=lr_vars.DefaultFont + ' bold', padx=0, pady=0)
        self.partNumDenyRbNext = tk.Checkbutton(self.last_frameCbx2, variable=lr_vars.VarPartNumDenyRbNext, text='deny',
                                                font=lr_vars.DefaultFont + ' bold', padx=0, pady=0)
        self.spin_RB_height = tk.Spinbox(self.last_frameCbx2, from_=1, to=99, textvariable=self.RB.heightVar, width=2,
                                         command=self.RB.set_height, font=lr_vars.DefaultFont + ' italic', background=lr_vars.Background)
        self.ButtonRB_note = tk.Button(self.last_frameCbx2, text='edit', command=lambda: lr_note(self.RB), width=3,
                                       font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)

        self.RbB1Cbx = tk.Checkbutton(self.rb_split_label, variable=lr_vars.VarRbB1, text='}', font=lr_vars.DefaultFont, padx=0, pady=0)
        self.RbB2Cbx = tk.Checkbutton(self.rb_split_label, variable=lr_vars.VarRbB2, text=']', font=lr_vars.DefaultFont, padx=0, pady=0)
        self.RbRstripCbx = tk.Checkbutton(self.last_frameCbx2, variable=lr_vars.VarRbRstrip, text='rstrip', font=lr_vars.DefaultFont, padx=0, pady=0)
        self.RbEndCbx = tk.Checkbutton(self.last_frameCbx2, variable=lr_vars.VarREnd, text='end', font=lr_vars.DefaultFont, padx=0, pady=0)

        # (6)
        self.t6 = tk.Label(self.mid_frame, text='(6)', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0, foreground='brown')
        self.ButtonShowParam = tk.Button(self.mid_frame, text='сформировать web_reg_save_param ',
                                         command=self.show_LR_Param, padx=0, pady=0, font=lr_vars.DefaultFont + ' bold', background='orange')

        self.cbxClipboard = tk.Checkbutton(self.mid_frame, variable=self.cbxWrspClipboard, text='clipboard',
                                           font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.filesStats_cbx = tk.Checkbutton(self.last_frame, variable=lr_vars.VarAllFilesStatistic, padx=0, pady=0, text='stats',
                                             font=lr_vars.DefaultFont + ' italic', command=self.set_folder)
        self.cbxClearShow = tk.Checkbutton(self.mid_frame, variable=self.cbxClearShowVar, text='clear',
                                           font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.cbxAutoShowParam = tk.Checkbutton(self.show_param_frame, variable=self.cbxWrspAutoCreate, text='auto',
                                               font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.cbxAutoNoteParam = tk.Checkbutton(self.mid_frame, variable=self.cbxNotepadWrsp, text='notepad',
                                               font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.cbxFileNamesNumsShow = tk.Checkbutton(self.show_param_frame, variable=lr_vars.VarFileNamesNumsShow,
                                                   text='name', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.cbxPopupWindow = tk.Checkbutton(self.last_frame, variable=lr_vars.VarShowPopupWindow, text='Window', padx=0, pady=0,
                                             background='orange', font=lr_vars.DefaultFont + ' italic bold')

        def force_unblock(*a) -> None:
            self._block_ = False
            self._block(False)

        self.unblock = tk.Button(self.last_frame, text='unblock', font=lr_vars.DefaultFont + ' bold', padx=0, pady=0, command=force_unblock)
        self.ButtonClearDown = tk.Button(self.last_frame, text='clearW', command=self.clear, font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.ButtonClearUp = tk.Button(self.last_frame, text='clearT', command=lambda: self.tk_text.delete(0.0, 'end'),
                                       font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.ButtonNote = tk.Button(self.last_frame, text='text', command=lambda: lr_other.openTextInEditor(self.tk_text.get('1.0', tk.END)),
                                    font=lr_vars.DefaultFont + ' italic', padx=0, pady=0)
        self.ButtonLog = tk.Button(self.last_frame, text='log', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0,
                                   command=lambda: subprocess.Popen([lr_vars.EDITOR['exe'], lr_vars.logFullName]))

        @lr_vars.T_POOL_decorator
        def editor_fn(*a):
            '''открыть в editor'''
            return subprocess.Popen([lr_vars.EDITOR['exe'], lr_files.get_file_with_kwargs(lr_vars.FilesWithParam)['File']['FullName']])

        self.ButtonParamFileOpen = tk.Button(self.last_frame, text='file(3)', font=lr_vars.DefaultFont + ' bold', padx=0, pady=0,
                                             command=editor_fn)
        self.Button_change_folder = tk.Button(self.last_frame, text='Folder', padx=0, pady=0, command=self.change_folder_ask,
                                              font=lr_vars.DefaultFont + ' italic bold')
        self.change_folder_cbx = tk.Checkbutton(self.last_frame, variable=lr_vars.VarIsSnapshotFiles, padx=0, pady=0,
                                                font=lr_vars.DefaultFont + ' italic', command=self.set_folder, text='inf')
        self.deny_file_cbx = tk.Checkbutton(self.last_frame, variable=lr_vars.VarAllowDenyFiles, padx=0, pady=0,
                                            font=lr_vars.DefaultFont + ' italic', command=self.set_folder, text='deny_ext')
        self.spin_toolTipTimeout = tk.Entry(self.last_frame, textvariable=lr_vars.VarToolTipTimeout, width=4, font=lr_vars.DefaultFont + ' italic')
        self.cbxOrdVersion = tk.Checkbutton(self.mid_frame, variable=lr_vars.VarOrdVersion, padx=0, pady=0, font=lr_vars.DefaultFont, text='ord')

        log_vals = list(lr_vars.loggingLevels.keys())
        self.comboLogger = ttk.Combobox(self.last_frame, textvariable=lr_vars.VarWindowLogger, justify='center',
                                        font=lr_vars.DefaultFont, width=max(len(k) for k in log_vals), style="BW.TButton")
        self.comboLogger['values'] = log_vals

        self.LBent_SplitList.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.LBent_SplitList.bind("<KeyRelease-Return>", self.comboParts_change)
        self.max_lb.bind("<KeyRelease-Return>", self.comboParts_change)

        self.RBent_SplitList.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.RBent_SplitList.bind("<KeyRelease-Return>", self.comboParts_change)
        self.max_rb.bind("<KeyRelease-Return>", self.comboParts_change)

        self.comboFiles.bind("<<ComboboxSelected>>", self.comboFiles_change)
        self.comboParts.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.comboParam.bind("<KeyRelease-Return>", self.get_files)

        def min_max_set(*a) -> None:
            '''max/min_inf'''
            if not lr_vars.FilesWithParam:
                return
            self.get_files()

        self.max_inf.bind("<<ComboboxSelected>>", min_max_set)
        self.min_inf.bind("<<ComboboxSelected>>", min_max_set)
        self.sortKey1.bind("<<ComboboxSelected>>", self.setSortKey1)
        self.sortKey2.bind("<<ComboboxSelected>>", self.setSortKey2)
        self.comboLogger.bind("<<ComboboxSelected>>", lambda *a: lr_vars.VarWindowLogger.set(self.comboLogger.get()))
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

        self._TT_text_comboFiles = '(3) - выбор файла из результатов поиска (2):lr_vars.FilesWithParam\n\t' \
                                   '# Window.comboFiles == lr_vars.FilesWithParam\n\t# lr_vars.VarFileName -> ' \
                                   'lr_vars.VarFile ->(4):lr_vars.VarFileText\n\t\t\t-> lr_vars.VarPartNum'

        lr_lib.gui.wrsp.tooltips.set_all_main_window_tooltip(self)  # создать все tooltip окна
        lr_lib.gui.wrsp.grid.grid_widj(self)  # grid всех виджетов окна

    def spl_cbx_cmd_lb(self, *a) -> None:
        '''lb SplitList widj'''
        if lr_vars.VarSplitListLB.get():
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

    def spl_cbx_cmd_rb(self, *a) -> None:
        '''rb SplitList widj'''
        if lr_vars.VarSplitListRB.get():
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

    def err_to_widgts(self, exc_type, exc_val, exc_tb, ern) -> None:
        '''отображение ошибки'''
        err = '{n}( {e} )'.format(n=ern, e=exc_val)
        lr_vars.Tk.title('{e} | {v}'.format(e=err, v=lr_vars.VERSION))
        self.last_frame.config(text='\n'.join(err.split('\n')[:5])[:500])
        # lr_tooltip.createToolTip(self.comboFiles, '\n'.join(lr_other._chunks(str(exc_val), 60)))

    def set_menu(self) -> None:
        '''menubar'''
        def set_editor() -> None:
            '''Select Editor'''
            __file = tk.filedialog.askopenfile()
            if __file:
                lr_vars.EDITOR['exe'] = __file.name

        self.menubar = tk.Menu(lr_vars.Tk)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Select Encode", command=lambda: lr_lib.gui.wrsp.top_wind.enc_wind(self))
        filemenu.add_command(label="Pools", command=lambda: lr_lib.gui.wrsp.top_wind.pool_wind(self))
        filemenu.add_command(label="Select Editor", command=set_editor)
        filemenu.add_command(label="Select Folder", command=self.change_folder_ask)
        filemenu.add_command(label="AllFiles list", command=lambda: lr_lib.gui.wrsp.top_wind.folder_wind(self))
        filemenu.add_command(label="LoadRunner action.c", command=lr_action.ActionWindow)
        filemenu.add_command(label="Help", command=lambda *a: lr_vars.Logger.info(lr_help.CODE + '\n' + lr_help.HELP))
        filemenu.add_command(label="Exit", command=lr_vars.Tk.destroy)
        self.menubar.add_cascade(label="Menu", menu=filemenu)
        lr_vars.Tk.config(menu=self.menubar)

    def set_rclick_menu(self) -> None:
        '''меню правой кнопки мыши'''
        lr_lib.gui.etc.sub_menu.rClickbinder(self)  # все tk
        for widj in dir(self):
            with contextlib.suppress(Exception):
                self.bind_class(getattr(self, widj), sequence='<Button-3>', func=lr_lib.gui.etc.sub_menu.rClicker, add='')

    def change_folder_ask(self, *args) -> None:
        '''смена директории поиска файлов'''
        d = filedialog.askdirectory()
        if d:
            lr_vars.VarFilesFolder.set(d)
            with self.block():
                lr_files.init()
            self.clear()

    def clear(self) -> None:
        '''очистить поля ввода'''
        self.show_frame_info_working()
        lr_vars.clearVars()
        self.LB.set('')
        self.RB.set('')
        self.comboFiles['values'] = [self.no_files_text]
        self.comboParts['values'] = [0]
        self.comboFiles.current(0)
        self.comboParts.current(0)
        lr_lib.gui.widj.lbrb5.LBRBText.set_label_text()
        self.set_comboFiles_width()
        self.sortKey1.set('Snapshot')
        self.sortKey2.set('Nums')
        self.last_frame_text_set()
        lr_tooltip.createToolTip(self.comboFiles, self._TT_text_comboFiles)
        lr_vars.Tk.title(lr_vars.VERSION)

    def last_frame_text_set(self) -> None:
        t = 'inf={i}: файлов={f} | MP: {pool}[{p_size}] | T: {tpool}[{tpool_size}] | {d}'.format(
            d=lr_vars.VarFilesFolder.get(), f=len(lr_vars.AllFiles), pool=lr_vars.M_POOL._name,
            i=len(list(lr_other.get_files_infs(lr_vars.AllFiles))), tpool_size=lr_vars.T_POOL._size,
            p_size=lr_vars.M_POOL._size, tpool=lr_vars.T_POOL._name)

        self.last_frame['text'] = t

    def clear_before_find_param_files(self) -> None:
        '''очистка виджетов перед поиском'''
        self.LB.set('')
        self.RB.set('')
        lr_lib.gui.widj.lbrb5.LBRBText.set_label_text()
        self.comboFiles['values'] = [self.no_files_text]
        self.comboParts['values'] = [-1]
        self.comboFiles.current(0)
        self.comboParts.current(0)
        lr_vars.VarLB.set('')
        lr_vars.VarRB.set('')

    def clip_add(self, text: str) -> None:
        '''буфер обмена'''
        self.clipboard_clear()
        self.clipboard_append(text)

    def add_message(self, levelname: str, text: str) -> None:
        '''сообщения в конец текста gui'''
        with contextlib.suppress(Exception):
            if lr_vars.loggingLevels[lr_vars.VarWindowLogger.get()] <= lr_vars.loggingLevels[levelname]:
                self.tk_text.insert(tk.END, '{}\n'.format(text))
                self.tk_text.see(tk.END)

    def print(self, levelname: str, text: str) -> None:
        '''сообщения в конец текста gui, в main потоке'''
        lr_vars.MainThreadUpdater.submit(lambda: self.add_message(levelname, text))

    def set_comboFiles_width(self) -> None:
        '''установка макс ширины комбо файлов(3)'''
        l = max(len(f) for f in self.comboFiles['values'])
        m = lr_vars.VarMaxComboFilesWidth.get()
        self.comboFiles.configure(width=l if l < m else m)

    def setSortKeys(self) -> None:
        '''задать комбо сортировки'''
        self.sortKey1['values'] = sorted(set(k for f in lr_vars.AllFiles for k in f))
        self.sortKey1.set(lr_vars.VarFileSortKey1.get())
        self.setSortKey1()
        self.sortKey2.set(lr_vars.VarFileSortKey2.get())

    def setSortKey1(self, *args) -> None:
        '''комбо сортировки 1'''
        lr_vars.VarFileSortKey1.set(self.sortKey1.get())
        self.sortKey2['values'] = list(set(k for f in itertools.chain(lr_vars.AllFiles, lr_vars.FilesWithParam)
                                           for k in f.get(self.sortKey1.get(), ())))
        self.sortKey2.set('')

    def setSortKey2(self, *args) -> None:
        '''комбо сортировки файлов'''
        lr_vars.VarFileSortKey2.set(self.sortKey2.get())
        if lr_vars.FilesWithParam:
            self.get_files()  # сортировка при поиске

    def show_frame_info_file(self) -> None:
        '''отображение всякой информации'''
        dt = lr_vars.VarWrspDict.get()

        lr_vars.Tk.title('"{param}", {Name}, {inf_nums} > Файлы(из {files_all} найдено {file_index}/{param_files}) | '
                         'Вхождения({param_part}/{param_count}, всего {param_all} в {_param_inf_all} inf) | {ver}'.format(
            ver=lr_vars.VERSION, **dt))

        self.main_frame['text'] = 'Snapshot{inf_nums}, Файл[{file_index}/{param_files}], ' \
                                  'Часть[{param_part}/{param_count}], {len} символов.'.format(**dt)

    def show_frame_info_working(self) -> None:
        '''отображение всякой информации'''
        self.main_frame['text'] = '{} | {} | ParamClipBoardSearchHotKey[{}]'.format(
            lr_vars.VarEncode.get(), time.strftime('%H:%M:%S'), lr_vars.FIND_PARAM_HOTKEY)
        self.last_frame['text'] = 'working ... %s' % lr_vars.VarFilesFolder.get()

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
        lr_vars.VarFileName.set(name)
        part = lr_vars.VarPartNum.get()
        self.comboPartsFill()
        self.comboParts.set(part if part else 0)
        self.comboParts_change()
        lr_tooltip.createToolTip(self.comboFiles, lr_other.file_string(lr_files.get_file_with_kwargs(
            lr_vars.FilesWithParam, Name=name)))

    def comboPartsFill(self) -> None:
        '''заполнить комбобокс (4)'''
        file = lr_vars.VarFile.get()
        if lr_vars.VarStrongSearchInFile.get():
            self.comboParts['values'] = file['Param']['Count_indexs']
        else:
            self.comboParts['values'] = list(range(file['Param']['Count']))
        lr_tooltip.createToolTip(
            lr_vars.Window.comboFiles, lr_other.file_string(lr_files.get_file_with_kwargs(
                lr_vars.FilesWithParam, Name=file['File']['Name'])))

    def comboParts_change(self, *args) -> None:
        '''смена комбо(4)'''
        if not lr_vars.FilesWithParam:
            return
        lr_vars.VarPartNum.set(int(self.comboParts.get()))
        lr_lib.gui.widj.lbrb5.LBRBText.set_LB_RB()
        self.show_frame_info_file()

    def firstOrLastFile(self, *args) -> None:
        '''выбрать первый/последный файл в (3)'''
        if not lr_vars.FilesWithParam:
            return
        i = (len(self.comboFiles['values']) - 1) if lr_vars.VarFirstLastFile.get() else 0
        self.comboFiles.current(i)
        self.comboFiles_change()

    def show_LR_Param(self, callback=None) -> str:
        '''показать web_reg_save_param (6)'''
        lr_vars.VarLB.set(self.LB.get())
        lr_vars.VarRB.set(self.RB.get())
        # с учетом редактирования LB/RB(5)
        web_reg_save_param = lr_param.create_web_reg_save_param(lr_param.wrsp_dict_creator())

        if web_reg_save_param:
            if self.cbxNotepadWrsp.get():
                lr_other.openTextInEditor(web_reg_save_param)
            if self.cbxWrspClipboard.get():
                self.clip_add(web_reg_save_param)
            if self.cbxClearShowVar.get():
                self.tk_text.delete(1.0, 'end')
            lr_vars.Logger.info('{s}\n{wrsp}\n{s}'.format(s=lr_vars.PRINT_SEPARATOR, wrsp=web_reg_save_param))
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
            lr_vars.VarParam.set(param, set_file=False, action=action)  # получить файлы с {param}

        self.comboFiles['values'] = [f['File']['Name'] for f in lr_vars.FilesWithParam] or [self.no_files_text]
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

    def set_folder(self, callback=None) -> None:
        '''установка folder'''
        self.clear()
        with self.block():
            lr_files.init()

        self.last_frame_text_set()
        self.setSortKey1()
        if callback:
            callback()

    def on_closing(self) -> None:
        '''не выходить, при открытых action.c окнах'''
        if not self.action_windows or tk.messagebox.askokcancel(
                'выход', "Есть открытые action.c окна\n{a}\n"
                         "все равно выйти?".format(a=', '.join(map(str, self.action_windows)))):
            self.destroy()
            lr_vars.Tk.destroy()

    @contextlib.contextmanager
    def block(self, w=('text', 'tk_text', 'min_inf', 'max_inf', 'unblock', 'cbxPopupWindow', 'last_frame', ), force=False) -> iter:
        '''заблокировать/разблокировать виджеты в gui'''
        try:
            if self._block_:
                yield
            else:
                if force:
                    self._block_ = True
                yield self._block(True, w=w)
        finally:
            if force:
                self._block_ = False
            if not self._block_:
                self._block(False, w=w)

    def _block(self, bl: bool, w=()) -> None:
        '''заблокировать/разблокировать виджеты в gui'''
        def set_block(state=('disabled' if bl else 'normal')):
            '''заблокировать/разблокировать'''
            for attr in dir(self):
                if not attr.startswith('_') and (attr not in w):
                    with contextlib.suppress(AttributeError, tk.TclError):
                        getattr(self, attr).configure(state=state)
            self.update()

        lr_vars.MainThreadUpdater.submit(set_block)

    def get_main_action(self) -> lr_action.ActionWindow:
        '''если открыто несколько action онон, какое вернуть'''
        try:
            action = self.action_windows[next(iter(self.action_windows))]
        except StopIteration:
            pass  # нет action онон
        else:
            return action

    def auto_update_action_pool_lab(self) -> None:
        '''обновление action.label с процентами и пулом'''
        if self.action_windows:
            for act in self.action_windows.values():
                if not hasattr(act, 'scroll_lab2'):
                    return

                if hasattr(lr_vars.T_POOL.pool, 'queue_in'):
                    pt = 'T:q_in\n{t} : {q_in}'.format(t=lr_vars.T_POOL._size, q_in=lr_vars.T_POOL.pool.queue_in.qsize())
                else:
                    pt = '  T\n  {t}'.format(t=lr_vars.T_POOL._size)

                if hasattr(lr_vars.M_POOL.pool, 'queue_in'):
                    pm = 'M:q_in\n{mp} : {q_in}'.format(mp=lr_vars.M_POOL._size, q_in=lr_vars.M_POOL.pool.queue_in.qsize())
                else:
                    pm = '  M {mp}'.format(mp=lr_vars.M_POOL._size)

                act.scroll_lab2.config(text='{p:>3}%\n\npool:\n\n{pt}\n\n{pm}'.format(
                    p=round(int(act.tk_text.linenumbers.linenum) / (act.tk_text.highlight_lines._max_line / 100)),
                    pt=pt, pm=pm))
