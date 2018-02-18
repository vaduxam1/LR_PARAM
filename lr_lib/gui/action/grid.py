# -*- coding: UTF-8 -*-
# grid виджетов action.с окна

import tkinter as tk


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
