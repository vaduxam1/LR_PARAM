# -*- coding: UTF-8 -*-
# action.с окно - шрифты и цвет

import itertools
import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.gui.action.act_replace
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

        self.background_color_combo.bind("<KeyRelease-Return>", self.background_color_set)
        self.background_color_combo.bind("<<ComboboxSelected>>", self.background_color_set)
        self.config(background=self.background_color_combo.get())
        return

    def bold_selection_set(self, *a) -> None:
        self.tk_text.set_tegs(parent=self)
        return

    def background_color_set(self, color='') -> None:
        """поменять цвет всех виджетов"""
        obs = [self, lr_vars.Window, ]
        obs = itertools.chain(*map(DiR, obs))

        for ob in obs:
            if color is None:
                if ob not in ColorCash:
                    try:
                        ColorCash[ob] = ob['background']
                    except Exception as ex:
                        continue
                background = self._rnd_color(color)
            elif not color:
                if ob in ColorCash:
                    background = ColorCash[ob]
                else:
                    background = self._rnd_color(color)
            else:
                background = self._rnd_color(color)

            try:
                ob.config(background=background)
            except Exception as ex:
                pass
            continue
        return

    def _rnd_color(self, color) -> str:
        """
        вернуть имя цвета
        :param color: None-случайный/False-оригинальный/str-"Red"
        :return: "Red"
        """
        if color is None:
            color = next(lr_lib.core.var.vars_highlight.ColorIterator)
        elif not color:
            color = self.background_color_combo.get()
        return color


ColorCash = {}
_Typ = ['utton', ]


def DiR(ob):
    """объекты для смены цвета"""
    for attr in dir(ob):
        ga = getattr(ob, attr)
        ta = type(ga)
        if not any(map(str(ta).__contains__, _Typ)):
            continue

        try:
            ga['background']
            assert hasattr(ga, 'config')
        except:
            continue

        yield ga
        if hasattr(ga, 'winfo_children') and (not callable(ga)):
            yield from DiR(ga.winfo_children())
        continue
    return
