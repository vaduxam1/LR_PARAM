# -*- coding: UTF-8 -*-
# action.с окно - скроллинг по тексту и запуск подсветки

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.gui.action.act_widj
import lr_lib.gui.widj.highlight_text


class ActScrollText(lr_lib.gui.action.act_widj.ActWidj):
    """скроллинг по тексту и запуск подсветки"""

    def __init__(self):
        lr_lib.gui.action.act_widj.ActWidj.__init__(self)

        self.tk_text = lr_lib.gui.widj.highlight_text.HighlightText(
            self, background=lr_lib.core.var.vars_highlight.Background, wrap=tk.NONE, bd=0,
        )

        self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
        self.tk_text.configure(yscrollcommand=self.report_position_Y, xscrollcommand=self.report_position_X, bd=0)

        self.highlight_cbx = tk.Checkbutton(
            self.cbx_bar, text='highlight', font=lr_vars.DefaultFont,
            background=lr_lib.core.var.vars_highlight.Background,
            variable=self.tk_text.highlight_var, command=self.tk_text.highlight_apply,
        )

        self.buttonColorReset = tk.Button(self.cbx_bar, text='reset', font=lr_vars.DefaultFont, command=self.resColor)

        self.highlight_After0 = tk.Entry(self.cbx_bar, font=lr_vars.DefaultFont, width=4)
        self.highlight_After1 = tk.Entry(self.cbx_bar, font=lr_vars.DefaultFont, width=4)
        self.highlight_After2 = tk.Entry(self.cbx_bar, font=lr_vars.DefaultFont, width=4)
        self.highlight_After0.insert(0, lr_lib.core.var.vars_highlight.HighlightAfter0)
        self.highlight_After1.insert(0, lr_lib.core.var.vars_highlight.HighlightAfter1)
        self.highlight_After2.insert(0, lr_lib.core.var.vars_highlight.HighlightAfter2)
        return

    def report_position_X(self, *argv) -> None:
        """get (beginning of) first visible line"""
        self.text_scrollx.set(*argv)
        self.report_position()
        return

    def report_position_Y(self, *argv) -> None:
        """get (beginning of) first visible line"""
        self.text_scrolly.set(*argv)
        self.report_position()
        return

    def report_position(self) -> None:
        """при скролле tk.Text, вывести номера линий, запустить подсветку"""
        top_bottom = (
            int(self.tk_text.index("@0,0").split('.', 1)[0]),
            int(self.tk_text.index("@0,%d" % self.tk_text.winfo_height()).split('.', 1)[0])
        )
        self.tk_text.highlight_lines.set_top_bottom(top_bottom)
        return

    def resColor(self) -> None:
        """сбросить self.tk_text.highlight_dict настройки цветов"""
        if messagebox.askquestion('сброс', 'сбросить текст настройки цветов?', parent=self) == 'yes':
            self.tk_text.reset_highlight()
        return
