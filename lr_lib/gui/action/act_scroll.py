# -*- coding: UTF-8 -*-
# action.с окно - скроллинг по тексту и запуск подсветки

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import messagebox

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

        self.highlight_cbx = tk.Checkbutton(
            self.cbx_bar, text='highlight', font=lr_vars.DefaultFont, background=lr_vars.Background,
            variable=self.tk_text.highlight_var, command=self.tk_text.highlight_apply)

        self.buttonColorReset = tk.Button(self.cbx_bar, text='reset', font=lr_vars.DefaultFont, command=self.resColor)

        self.highlight_Thread = tk.Checkbutton(
            self.cbx_bar, text='', variable=lr_vars.HighlightThread, font=lr_vars.DefaultFont,
            command=lambda *a: self.tk_text.highlight_lines.set_thread_attrs())
        self.highlight_LineThread = tk.Checkbutton(
            self.cbx_bar, text='', variable=lr_vars.LineTagAddThread, font=lr_vars.DefaultFont,
            command=lambda *a: self.tk_text.highlight_lines.set_thread_attrs())
        self.highlight_TagThread = tk.Checkbutton(
            self.cbx_bar, text='', variable=lr_vars.TagAddThread, font=lr_vars.DefaultFont,
            command=lambda *a: self.tk_text.highlight_lines.set_thread_attrs())
        self.highlight_MThread = tk.Checkbutton(
            self.cbx_bar, text='', variable=lr_vars.HighlightMPool, font=lr_vars.DefaultFont,
            command=lambda *a: self.tk_text.highlight_lines.set_thread_attrs())

        self.highlight_LinesPortionSize = tk.Spinbox(
            self.cbx_bar, from_=0, to=100, width=2, font=lr_vars.DefaultFont,
            textvariable=lr_vars.HighlightLinesPortionSize)

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

    def resColor(self) -> None:
        """сбросить self.tk_text.highlight_dict настройки цветов"""
        if messagebox.askquestion('сброс', 'сбросить текст настройки цветов?', parent=self) == 'yes':
            self.tk_text.reset_highlight()
