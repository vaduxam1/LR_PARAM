# -*- coding: UTF-8 -*-
# action.с окно - шрифты и цвет

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import messagebox

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.action.act_replace as lr_act_replace
import lr_lib.etc.help as lr_help


class ActFont(lr_act_replace.ActReplaceRemove):
    """шрифты и цвет"""

    def __init__(self):
        lr_act_replace.ActReplaceRemove.__init__(self)

        self.highlight_cbx = tk.Checkbutton(self.cbx_bar, text='highlight', font=lr_vars.DefaultFont,
                                            background=lr_vars.Background,
                                            variable=self.tk_text.highlight_var, command=self.tk_text.highlight_apply)

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

    def bold_selection_set(self, *a) -> None:
        self.tk_text.set_tegs(parent=self)

    def background_color_set(self, *args, color='') -> None:
        """установить цвет фона"""
        if color is None:  # смена по кругу
            color = next(lr_vars.ColorIterator)
        if not color:  # выбранный
            color = self.background_color_combo.get()

        self.config(background=color)
        self.scroll_lab2.config(background=color)
        self.tk_text.config(background=color)
        self.tk_text.linenumbers.config(background=color)

    def resColor(self) -> None:
        """сбросить self.tk_text.highlight_dict настройки цветов"""
        if messagebox.askquestion('сброс', 'сбросить текст настройки цветов?', parent=self) == 'yes':
            self.tk_text.reset_highlight()
