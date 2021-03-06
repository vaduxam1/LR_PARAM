# -*- coding: UTF-8 -*-
# action.с окно - переменные которые надо создать первыми

import configparser
import os
import tkinter as tk

import lr_lib
import lr_lib.core.action.main_awal
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.gui.action.act_toplevel


class ActVar(lr_lib.gui.action.act_toplevel.ActToplevel):
    """
    переменные которые надо создать первыми
        main_action.ActionWindow
        act_win.ActWin
        act_any.ActAny
        act_goto.ActGoto
        act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
        act_serializ.TkTextWebSerialization
        act_backup.ActBackup
        act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
      + act_var.ActVar
        act_toplevel.ActToplevel
        tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_toplevel.ActToplevel.__init__(self)
        self.id_ = id(self)

        # ActionWebsAndLines
        self.web_action = lr_lib.core.action.main_awal.ActionWebsAndLines(action=self)
        self.action_file = None  # путь_имя текущего action.c

        self.usr_file = '{}.usr'.format(os.path.basename(os.path.dirname(lr_vars.VarFilesFolder.get())))
        self.usr_config = self.get_usr_file()

        self.transaction = []  # имена action transaction

        self.SearchReplace_searchVar = tk.StringVar(value='')
        self.SearchReplace_replaceVar = tk.StringVar(value='')
        self.final_wnd_var = tk.BooleanVar(value=lr_vars.DefaultActionFinalWind)
        self.force_ask_var = tk.BooleanVar(value=lr_vars.DefaultActionForceAsk)
        self.no_var = tk.BooleanVar(value=lr_vars.DefaultActionNoVar)
        self.max_inf_cbx_var = tk.BooleanVar(value=lr_vars.DefaultActionMaxSnapshot)
        self.add_inf_cbx_var = lr_vars.DefaultActionAddSnapshot
        self.force_yes_inf = tk.BooleanVar(value=lr_vars.DefaultActionForceYes)

        self.font_var = tk.StringVar(value=lr_vars.DefaultActionHighlightFont)
        self.background_var = tk.StringVar(value=lr_lib.core.var.vars_highlight.Background)
        self.size_var = tk.IntVar(value=lr_vars.DefaultActionHighlightFontSize)

        self.weight_var = tk.BooleanVar(value=lr_vars.DefaultActionHighlightFontBold)
        self.underline_var = tk.BooleanVar(value=lr_vars.DefaultActionHighlightFontUnderline)
        self.slant_var = tk.BooleanVar(value=lr_vars.DefaultHighlightActionFontSlant)
        self.overstrike_var = tk.BooleanVar(value=lr_vars.DefaultHighlightActionFontOverstrike)
        return

    def get_usr_file(self) -> configparser.ConfigParser:
        """
        result_folder = self.get_usr_file()['General']['LastResultDir']
        """
        config = configparser.ConfigParser()
        config.read(os.path.join(os.getcwd(), self.usr_file))
        return config
