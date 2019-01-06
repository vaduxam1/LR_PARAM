# -*- coding: UTF-8 -*-
# action.с окно - шрифты и цвет

import itertools
import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.gui.action.act_replace
import lr_lib.gui.etc.color_change
import lr_lib.core.var.vars as lr_vars


class ActFont(lr_lib.gui.action.act_replace.ActReplaceRemove):
    """шрифты и цвет"""

    def __init__(self):
        lr_lib.gui.action.act_replace.ActReplaceRemove.__init__(self)

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
        self.background_color_combo['values'] = list(sorted(lr_lib.etc.help.COLORS.keys()))

        self.background_color_combo.bind(
            "<KeyRelease-Return>", lambda *a: lr_lib.gui.etc.color_change.background_color_set(
                self, color=self.background_color_combo.get(), obs=[self.tk_text, ],
            ))
        self.background_color_combo.bind(
            "<<ComboboxSelected>>", lambda *a: lr_lib.gui.etc.color_change.background_color_set(
            self, color=self.background_color_combo.get(), _types=('Text', 'rame', 'bel', ),
            ))
        self.config(background=self.background_color_combo.get())
        return

    def bold_selection_set(self, *a) -> None:
        self.tk_text.set_tegs(parent=self)
        return
