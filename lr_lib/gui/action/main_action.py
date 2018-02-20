# -*- coding: UTF-8 -*-
# action.с окно

import os
import contextlib

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import messagebox

import lr_lib.gui.action.tooltips as lr_a_tooltips
import lr_lib.gui.action.act_win as lr_act_win
import lr_lib.gui.action.act_other as lr_act_other
import lr_lib.gui.wrsp.top_wind as lr_top_wind
import lr_lib.gui.widj.wrsp_setting as lr_wrsp_setting
import lr_lib.gui.etc.action_lib as lr_action_lib
import lr_lib.gui.etc.gui_other as lr_gui_other
import lr_lib.gui.etc.sub_menu as lr_sub_menu
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.core.etc.other as lr_other
import lr_lib.etc.help as lr_help


class ActionWindow(lr_act_win.ActWin):
    '''окно action.c'''

    def __init__(self):
        lr_act_win.ActWin.__init__(self)

        self.scroll_lab2 = ttk.Label(self, text='0 %', background=lr_vars.Background)

        self.help1 = tk.Label(self, text='?', foreground='grey')
        self.help2 = tk.Label(self, text='?', foreground='grey')
        self.help3 = tk.Label(self, text='?', foreground='grey')

        #
        self.inf_combo = ttk.Combobox(self.inf_bar, justify='center', font=lr_vars.DefaultFont)
        self.inf_combo.bind("<KeyRelease-Return>", self.goto_inf)
        self.inf_combo.bind("<<ComboboxSelected>>", self.goto_inf)

        #
        self.wrsp_combo = ttk.Combobox(self.wrsp_bar, justify='center', font=lr_vars.DefaultFont)

        self.wrsp_combo.bind("<KeyRelease-Return>", self.goto_wrsp)
        self.wrsp_combo.bind("<<ComboboxSelected>>", self.goto_wrsp)

        self.param_combo = ttk.Combobox(self.wrsp_bar, justify='center', font=lr_vars.DefaultFont)

        self.param_combo.bind("<KeyRelease-Return>", self.goto_param)
        self.param_combo.bind("<<ComboboxSelected>>", self.goto_param)

        #
        self.transaction_combo = ttk.Combobox(self.transaction_bar, justify='center', font=lr_vars.DefaultFont)

        self.transaction_combo.bind("<KeyRelease-Return>", self.goto_transaction)
        self.transaction_combo.bind("<<ComboboxSelected>>", self.goto_transaction)

        self.font_size_entry = tk.Spinbox(self.font_toolbar, width=2, justify='center', from_=0, to=99,
                                          command=self.tk_text.set_font,
                                          textvariable=self.tk_text.size_var, font=lr_vars.DefaultFont)

        self.font_size_entry.bind("<KeyRelease-Return>", self.tk_text.set_font)

        self.selection_font_size_entry = tk.Spinbox(self.font_toolbar, width=2, justify='center', from_=0, to=99,
                                                    textvariable=self.size_var,
                                                    font=lr_vars.DefaultFont,
                                                    command=lambda *a: self.tk_text.set_tegs(parent=self, remove=False))

        self.selection_font_size_entry.bind("<KeyRelease-Return>",
                                            lambda *a: self.tk_text.set_tegs(parent=self, remove=False))

        self.bold_cbx = tk.Checkbutton(self.font_toolbar, text='', font=lr_vars.DefaultFont + ' bold',
                                       variable=self.tk_text.weight_var, command=self.tk_text.set_font)
        self.slant_cbx = tk.Checkbutton(self.font_toolbar, text='', font=lr_vars.DefaultFont + ' italic',
                                        variable=self.tk_text.slant_var, command=self.tk_text.set_font)
        self.underline_cbx = tk.Checkbutton(self.font_toolbar, text='', font=lr_vars.DefaultFont + ' underline',
                                            variable=self.tk_text.underline_var, command=self.tk_text.set_font)
        self.overstrike_cbx = tk.Checkbutton(self.font_toolbar, text='', font=lr_vars.DefaultFont + ' overstrike',
                                             variable=self.tk_text.overstrike_var, command=self.tk_text.set_font)

        self.selection_bold_cbx = tk.Checkbutton(self.font_toolbar, text='', font=lr_vars.DefaultFont + ' bold',
                                                 variable=self.weight_var, command=self.bold_selection_set)
        self.selection_slant_cbx = tk.Checkbutton(self.font_toolbar, text='', font=lr_vars.DefaultFont + ' italic',
                                                  variable=self.slant_var, command=self.bold_selection_set)
        self.selection_underline_cbx = tk.Checkbutton(self.font_toolbar, text='',
                                                      font=lr_vars.DefaultFont + ' underline',
                                                      variable=self.underline_var, command=self.bold_selection_set)
        self.selection_overstrike_cbx = tk.Checkbutton(self.font_toolbar, text='',
                                                       font=lr_vars.DefaultFont + ' overstrike',
                                                       variable=self.overstrike_var, command=self.bold_selection_set)

        self.font_combo = ttk.Combobox(self.font_toolbar, textvariable=self.tk_text.font_var, justify='center',
                                       font=lr_vars.DefaultFont)
        self.font_combo['values'] = list(sorted(tk.font.families()))

        self.font_combo.bind("<KeyRelease-Return>", self.tk_text.set_font)
        self.font_combo.bind("<<ComboboxSelected>>", self.tk_text.set_font)

        self.selection_font_combo = ttk.Combobox(self.font_toolbar, textvariable=self.font_var, justify='center',
                                                 font=lr_vars.DefaultFont)
        self.selection_font_combo['values'] = list(sorted(tk.font.families()))

        self.selection_font_combo.bind("<KeyRelease-Return>", self.bold_selection_set)
        self.selection_font_combo.bind("<<ComboboxSelected>>", self.bold_selection_set)

        self.tk_text.set_font()
        self.bold_selection_set()

        self.background_color_combo = ttk.Combobox(self.cbx_bar, textvariable=self.background_var, justify='center',
                                                   font=lr_vars.DefaultFont)
        self.background_color_combo['values'] = list(sorted(lr_help.COLORS.keys()))

        self.background_color_combo.bind("<KeyRelease-Return>", self.background_color_set)
        self.background_color_combo.bind("<<ComboboxSelected>>", self.background_color_set)
        self.config(background=self.background_color_combo.get())

        self.search_button = tk.Button(self.toolbar, text='> Поиск >', command=self.search_in_action,
                                       font=lr_vars.DefaultFont)

        self.unblock = tk.Button(self.file_bar, text='unblock', font=lr_vars.DefaultFont + ' bold',
                                 command=lambda *a: self._block(False))
        self.backup_open_button = tk.Button(self.file_bar, text='backup_open', background='orange',
                                            font=lr_vars.DefaultFont + ' bold',
                                            command=lambda *a: self.open_action_dialog(title=True,
                                                                                       folder=lr_vars.BackupFolder))
        self.save_action_button = tk.Button(self.file_bar, text='save', font=lr_vars.DefaultFont + ' bold',
                                            command=self.save_action_file)
        self.open_button = tk.Button(self.file_bar, text='open', font=lr_vars.DefaultFont,
                                     command=self.open_action_dialog)
        self.editor_button = tk.Button(self.file_bar, text='editor', font=lr_vars.DefaultFont + ' bold',
                                       command=lambda: lr_other.openTextInEditor(self.tk_text.get(1.0, tk.END)))

        self.scroll_lab = ttk.Label(self, text='0')

        self.SearchReplace_searchCombo = ttk.Combobox(self.toolbar, textvariable=self.SearchReplace_searchVar,
                                                      justify='center', font=lr_vars.DefaultFont + ' italic',
                                                      foreground="purple")
        self.SearchReplace_replaceCombo = ttk.Combobox(self.toolbar, textvariable=self.SearchReplace_replaceVar,
                                                       justify='center', font=lr_vars.DefaultFont, foreground="maroon")
        self.SearchReplace_searchCombo['values'] = ['']
        self.SearchReplace_replaceCombo['values'] = ['']

        self.auto_param_creator_button = tk.Button(self.toolbar, text='Найти param LB=',
                                                   font=lr_vars.DefaultFont + ' bold',
                                                   command=self.auto_param_creator, background='orange')

        self.re_auto_param_creator_button = tk.Button(self.toolbar, text='Найти param RegExp',
                                                      font=lr_vars.DefaultFont + ' bold',
                                                      command=self.re_auto_param_creator, background='orange')

        self.final_wnd_cbx = tk.Checkbutton(self.toolbar, text='final', font=lr_vars.DefaultFont,
                                            variable=self.final_wnd_var)
        self.wrsp_setting = tk.Button(self.toolbar, text='wrsp_setting', font=lr_vars.DefaultFont + ' bold',
                                      command=lambda *a: lr_wrsp_setting.WrspSettingWindow(parent=self))

        self.resp_btn = tk.Button(self.toolbar, text='файлы ответов', font=lr_vars.DefaultFont,
                                  command=lambda *a: lr_action_lib.snapshot_files(self.tk_text, i_num=1))

        def force_ask_cmd(*a) -> None:
            if self.force_ask_var.get():
                self.no_var.set(0)

        self.force_ask_cbx = tk.Checkbutton(self.toolbar, text='Ask', font=lr_vars.DefaultFont,
                                            variable=self.force_ask_var,
                                            command=force_ask_cmd)

        self.highlight_cbx = tk.Checkbutton(self.cbx_bar, text='highlight', font=lr_vars.DefaultFont,
                                            background=lr_vars.Background,
                                            variable=self.tk_text.highlight_var, command=self.tk_text.set_highlight)

        def no_var_cmd(*a) -> None:
            if self.no_var.get():
                self.force_ask_var.set(0)

        self.no_cbx = tk.Checkbutton(self.toolbar, text='NoAsk', font=lr_vars.DefaultFont, variable=self.no_var,
                                     command=no_var_cmd)

        self.SearchReplace_button = tk.Button(self.toolbar, text='> замена >', font=lr_vars.DefaultFont,
                                              command=self._replace_button_set)
        self.buttonColorReset = tk.Button(self.cbx_bar, text='reset', font=lr_vars.DefaultFont, command=self.resColor)
        self.highlight_Thread = tk.Checkbutton(self.cbx_bar, text='', variable=lr_vars.HighlightThread,
                                               font=lr_vars.DefaultFont)
        self.highlight_LineThread = tk.Checkbutton(self.cbx_bar, text='', variable=lr_vars.LineTagAddThread,
                                                   font=lr_vars.DefaultFont)
        self.highlight_TagThread = tk.Checkbutton(self.cbx_bar, text='', variable=lr_vars.TagAddThread,
                                                  font=lr_vars.DefaultFont)
        self.highlight_MThread = tk.Checkbutton(self.cbx_bar, text='', variable=lr_vars.HighlightMPool,
                                                font=lr_vars.DefaultFont)
        self.highlight_LinesPortionSize = tk.Spinbox(self.cbx_bar, from_=0, to=100, width=2, font=lr_vars.DefaultFont,
                                                     textvariable=lr_vars.HighlightLinesPortionSize)

        self.max_inf_cbx = tk.Checkbutton(self.toolbar, text='ограничить\nmax inf', font=lr_vars.DefaultFont + ' bold',
                                          variable=self.max_inf_cbx_var, command=self.max_inf_set)
        self.add_inf_cbx = tk.Checkbutton(self.toolbar, anchor=tk.E, text='max\nmode', font=lr_vars.DefaultFont,
                                          variable=self.add_inf_cbx_var)

        self.lr_legend = tk.Button(self.toolbar, text='web_legend', font=lr_vars.DefaultFont, command=self.legend)
        self.btn_all_files = tk.Button(self.toolbar, text='все файлы', font=lr_vars.DefaultFont,
                                       command=lambda *a: lr_top_wind.folder_wind(self))
        self.lr_think_time = tk.Button(self.toolbar, text='lr_think_time', font=lr_vars.DefaultFont + ' bold',
                                       command=self.thinktime_remove)
        self.lr_report_B = tk.Button(self.toolbar, text='reportB', font=lr_vars.DefaultFont + ' bold',
                                     command=lambda *a: lr_gui_other.repB(self.tk_text))
        self.lr_report_A = tk.Button(self.toolbar, text='reportA', font=lr_vars.DefaultFont + ' bold',
                                     command=lambda *a: lr_gui_other.repA(self.tk_text))

        self.transaction_rename = tk.Button(self.toolbar, text='rename\ntransaction',
                                            font=lr_vars.DefaultFont + ' bold',
                                            background='orange', command=self.all_transaction_rename)
        self.dummy_button = tk.Button(self.toolbar, text="Snapshot remove", font=lr_vars.DefaultFont + ' bold',
                                      background='orange', command=self.dummy_btn_cmd)
        self.force_yes_inf_checker_cbx = tk.Checkbutton(self.toolbar, text='fYes', font=lr_vars.DefaultFont,
                                                        variable=self.force_yes_inf)

        self.post_init()


    def post_init(self):
        self.grid_widj()
        lr_a_tooltips.set_all_action_window_tooltip(self)  # создать все tooltip окна

        for widj in (self.search_res_combo, self.SearchReplace_searchCombo, self.SearchReplace_replaceCombo,
                     self.search_entry,):
            with contextlib.suppress(Exception):  # виджетам доступно меню мыши
                self.bind_class(widj, sequence='<Button-3>', func=lr_sub_menu.rClicker, add='')

        lr_act_other.auto_update_action_info_lab(
            self=self, config=self.scroll_lab2.config, tk_kext=self.tk_text, id_=self.id_,
            timeout=lr_vars.InfoLabelUpdateTime.get(), check_run=lr_vars.Window.action_windows.__contains__,
            title=self.title, _set_title=self._set_title)


    def grid_widj(self):
        '''grid всех виджетов action.с окна'''
        self.search_entry.grid(row=5, column=0, columnspan=8, sticky=tk.NSEW)
        self.search_button.grid(row=5, column=8, sticky=tk.NSEW)
        self.down_search_button.grid(row=5, column=9, sticky=tk.NSEW)
        self.search_res_combo.grid(row=5, column=10, sticky=tk.NSEW, columnspan=3)
        self.up_search_button.grid(row=5, column=13, sticky=tk.NSEW)

        self.backup_open_button.grid(row=5, column=16, columnspan=2, sticky=tk.NSEW)
        self.save_action_button.grid(row=6, column=17, sticky=tk.NSEW)

        self.highlight_cbx.grid(row=1, column=1, sticky=tk.NSEW, columnspan=5)
        self.background_color_combo.grid(row=2, column=1, sticky=tk.NSEW, columnspan=5)
        self.buttonColorReset.grid(row=3, column=1, sticky=tk.NSEW, columnspan=5)
        self.highlight_Thread.grid(row=4, column=1, sticky=tk.NSEW)
        self.highlight_LineThread.grid(row=4, column=2, sticky=tk.NSEW)
        self.highlight_TagThread.grid(row=4, column=3, sticky=tk.NSEW)
        self.highlight_MThread.grid(row=4, column=4, sticky=tk.NSEW)
        self.highlight_LinesPortionSize.grid(row=4, column=5, sticky=tk.NSEW)

        self.open_button.grid(row=6, column=16, sticky=tk.NSEW)
        self.editor_button.grid(row=7, column=16, sticky=tk.NSEW, columnspan=2)
        self.no_cbx.grid(row=7, column=10, sticky=tk.W)
        self.auto_param_creator_button.grid(row=7, column=8, sticky=tk.NSEW)
        self.re_auto_param_creator_button.grid(row=8, column=8, sticky=tk.NSEW)
        self.force_ask_cbx.grid(row=8, column=10, sticky=tk.W)
        self.unblock.grid(row=9, column=17, sticky=tk.NSEW)
        self.final_wnd_cbx.grid(row=8, column=12, sticky=tk.W)
        self.wrsp_setting.grid(row=7, column=9, sticky=tk.NSEW)
        self.resp_btn.grid(row=7, column=3, sticky=tk.NSEW)

        self.font_size_entry.grid(row=12, column=4, sticky=tk.NSEW)
        self.font_combo.grid(row=10, column=0, columnspan=10, sticky=tk.NSEW)
        self.bold_cbx.grid(row=12, column=5, sticky=tk.NSEW)
        self.overstrike_cbx.grid(row=12, column=6, sticky=tk.NSEW)
        self.underline_cbx.grid(row=12, column=7, sticky=tk.NSEW)
        self.slant_cbx.grid(row=12, column=8, sticky=tk.NSEW)
        self.backup_entry.grid(row=9, column=16, sticky=tk.NSEW)

        self.selection_font_combo.grid(row=11, column=0, columnspan=10, sticky=tk.NSEW)
        self.selection_font_size_entry.grid(row=13, column=4, sticky=tk.NSEW)
        self.selection_bold_cbx.grid(row=13, column=5, sticky=tk.NSEW)
        self.selection_overstrike_cbx.grid(row=13, column=6, sticky=tk.NSEW)
        self.selection_underline_cbx.grid(row=13, column=7, sticky=tk.NSEW)
        self.selection_slant_cbx.grid(row=13, column=8, sticky=tk.NSEW)

        self.SearchReplace_searchCombo.grid(row=6, column=0, columnspan=8, sticky=tk.NSEW)
        self.SearchReplace_replaceCombo.grid(row=6, column=9, columnspan=8, sticky=tk.NSEW)
        self.SearchReplace_button.grid(row=6, column=8, sticky=tk.NSEW)

        self.toolbar.grid(row=2, column=0, sticky=tk.N, columnspan=100)

        self.middle_bar.grid(row=3, column=0, sticky=tk.N)
        self.inf_bar.grid(row=3, column=1, sticky=tk.N)
        self.transaction_bar.grid(row=3, column=2, sticky=tk.E)
        self.wrsp_bar.grid(row=3, column=3, sticky=tk.W)

        self.file_bar.grid(row=5, column=20, sticky=tk.NSEW, rowspan=5)
        self.cbx_bar.grid(row=5, column=50, sticky=tk.NSEW, rowspan=5)
        self.font_toolbar.grid(row=5, column=21, sticky=tk.NSEW, rowspan=4)

        self.text_scrolly.grid(row=0, column=201, sticky=tk.NSEW)
        self.text_scrollx.grid(row=1, column=0, sticky=tk.NSEW, columnspan=201)
        self.scroll_lab.grid(row=1, column=300, sticky=tk.NSEW)
        self.scroll_lab2.grid(row=2, column=300, sticky=tk.NSEW, rowspan=2)

        self.inf_combo.grid(row=1, column=1, sticky=tk.NSEW)
        self.transaction_combo.grid(row=1, column=2, sticky=tk.NSEW)
        self.wrsp_combo.grid(row=1, column=3, sticky=tk.NSEW)
        self.param_combo.grid(row=1, column=4, sticky=tk.NSEW)

        self.help1.grid(row=1, column=201, sticky=tk.NSEW)
        self.help2.grid(row=2, column=201, sticky=tk.NSEW)
        self.help3.grid(row=3, column=201, sticky=tk.NSEW)

        self.tk_text.grid(row=0, column=0, sticky=tk.NSEW, columnspan=201)
        self.tk_text.linenumbers.grid(row=0, column=300, sticky=tk.NS)
        self.tk_text.linenumbers.config(width=30)

        self.max_inf_cbx.grid(row=7, column=1, sticky=tk.NSEW, rowspan=2)
        self.add_inf_cbx.grid(row=7, column=2, sticky=tk.NSEW, rowspan=2)
        self.dummy_button.grid(row=7, column=13, sticky=tk.NSEW)
        self.force_yes_inf_checker_cbx.grid(row=7, column=12, sticky=tk.W)
        self.lr_legend.grid(row=8, column=9, sticky=tk.NSEW)
        self.btn_all_files.grid(row=8, column=3, sticky=tk.NSEW)
        self.lr_think_time.grid(row=8, column=13, sticky=tk.NSEW)
        self.lr_report_B.grid(row=8, column=4, sticky=tk.NSEW)
        self.lr_report_A.grid(row=7, column=4, sticky=tk.NSEW)
        self.transaction_rename.grid(row=7, column=5, sticky=tk.NSEW, rowspan=2)


    def widj_reset(self) -> None:
        '''обновить виджеты'''
        self.transaction.clear()
        self.transaction.extend(self.get_transaction(self.tk_text.get(1.0, tk.END)))
        self.transaction_combo_set()
        self.drop_file_none_inf_num_in_action()
        self.inf_combo_set()
        self.toolbar['text'] = self.param_counter(all_param_info=False)
        self.set_title()
        self.set_combo_len()


    @lr_vars.T_POOL_decorator
    def goto_inf(self, *a) -> None:
        with contextlib.suppress(tk.TclError):
            self.search_in_action(word=lr_param.Snap.format(num=self.inf_combo.get().strip()), hist=False)


    @lr_vars.T_POOL_decorator
    def goto_transaction(self, *args) -> None:
        with contextlib.suppress(tk.TclError):
            self.search_in_action(word=self.transaction_combo.get(), hist=False)


    @lr_vars.T_POOL_decorator
    def goto_param(self, *args) -> None:
        with contextlib.suppress(tk.TclError):
            self.search_in_action(word=self.param_combo.get(), hist=False)


    @lr_vars.T_POOL_decorator
    def goto_wrsp(self, *args) -> None:
        with contextlib.suppress(tk.TclError):
            self.search_in_action(word=self.wrsp_combo.get(), hist=False)


    @lr_vars.T_POOL_decorator
    def bold_selection_set(self, *a) -> None:
        self.tk_text.set_tegs(parent=self)


    def background_color_set(self, *args, color='') -> None:
        '''установить цвет фона'''
        if color is None:  # смена по кругу
            color = next(lr_vars.ColorIterator)
        if not color:  # выбранный
            color = self.background_color_combo.get()

        self.config(background=color)
        self.scroll_lab2.config(background=color)
        self.tk_text.config(background=color)
        self.tk_text.linenumbers.config(background=color)

    def clear_text(self) -> None:
        '''очистить tk_text'''
        if messagebox.askquestion('очистить', 'очистить окно?', parent=self) == 'yes':
            self.backup()
            self.tk_text.delete(1.0, tk.END)


    def resColor(self) -> None:
        '''сбросить self.tk_text.highlight_dict настройки цветов'''
        if messagebox.askquestion('сброс', 'сбросить текст настройки цветов?', parent=self) == 'yes':
            self.tk_text.reset_highlight()


    @lr_vars.T_POOL_decorator
    def open_action_dialog(self, *a, title=False, folder=os.getcwd()) -> None:
        '''открыть файл'''
        if title:
            af = tk.filedialog.askopenfilename(initialdir=folder, parent=self, filetypes=(
                ("%s_backup_*.c" % self.id_, "%s_backup_*.c" % self.id_), ("all", "*.*")),
                                               title='backup({})'.format(self.id_))
        else:
            af = tk.filedialog.askopenfilename(initialdir=folder, parent=self, filetypes=(
                ("action.c", "*.c"), ("all", "*.*")))
        if af:
            self.open_action(file=af)


    def inf_combo_set(self) -> None:
        self.inf_combo['values'] = list(self.action_infs)
        if self.inf_combo['values']:
            self.inf_combo.current(0)


    def wrsp_combo_set(self) -> None:
        self.wrsp_combo['values'] = list(self.web_action.websReport.wrsp_and_param_names.keys())


    def param_combo_set(self) -> None:
        with contextlib.suppress(Exception):
            self.param_combo['values'] = list(self.web_action.websReport.wrsp_and_param_names.values())


    def transaction_combo_set(self) -> None:
        self.transaction_combo['values'] = self.transaction


    def set_combo_len(self):
        if lr_vars.Window._block_:
            return
        min_len = lr_vars.VarActComboLenMin.get()
        max_len = lr_vars.VarActComboLenMax.get()
        for w in dir(self):
            attr = getattr(self, w)
            if isinstance(attr, ttk.Combobox):
                m = max([len(str(f)) for f in attr['values']] or [min_len])
                attr.configure(width=m if min_len <= m <= max_len else min_len if m < min_len else max_len)
        self.selection_font_combo.configure(width=20)
        self.font_combo.configure(width=20)


    def set_title(self) -> None:
        self.title('{} {} undo: ctrl-z / redo: ctrl-y)'.format(self._set_title(), lr_vars.VERSION))


    def _set_title(self) -> str:
        return '{a} | {i} | backup={b} |'.format(a=self.action_file, b=self._backup_index, i=self.id_)
