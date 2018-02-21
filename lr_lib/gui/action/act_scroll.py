# -*- coding: UTF-8 -*-
# action.с окно - скроллинг по тексту и запуск подсветки

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.gui.widj.highlight_text as lr_highlight_text
import lr_lib.gui.action.act_widj as lr_act_widj
import lr_lib.core.var.vars as lr_vars


class ActScrollText(lr_act_widj.ActWidj):
    """скроллинг по тексту и запуск подсветки"""

    def __init__(self):
        lr_act_widj.ActWidj.__init__(self)

        self.tk_text = lr_highlight_text.HighlightText(self, background=lr_vars.Background, wrap=tk.NONE, bd=0)

        self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
        self.tk_text.configure(yscrollcommand=self.report_position_Y, xscrollcommand=self.report_position_X, bd=0)

    def report_position_X(self, *argv) -> None:
        """get (beginning of) first visible line"""
        self.text_scrollx.set(*argv)
        self.report_position()

    def report_position_Y(self, *argv) -> None:
        """get (beginning of) first visible line"""
        self.text_scrolly.set(*argv)
        self.report_position()

    def report_position(self) -> None:
        """при скролле tk.Text, вывести номера линий, запустить подсветку"""
        top_bottom = (
            int(self.tk_text.index("@0,0").split('.', 1)[0]),
            int(self.tk_text.index("@0,%d" % self.tk_text.winfo_height()).split('.', 1)[0])
        )
        self.tk_text.highlight_lines.set_top_bottom(top_bottom)

