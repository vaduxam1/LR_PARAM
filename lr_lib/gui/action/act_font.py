# -*- coding: UTF-8 -*-
# action.с окно - шрифты и цвет

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.gui.action.act_replace
import lr_lib.gui.etc.color_change


class ActFont(lr_lib.gui.action.act_replace.ActReplaceRemove):
    """
    шрифты и цвет
        main_action.ActionWindow
        act_win.ActWin
        act_any.ActAny
        act_goto.ActGoto
      + act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
        act_serializ.TkTextWebSerialization
        act_backup.ActBackup
        act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
        act_var.ActVar
        act_toplevel.ActToplevel
        tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_replace.ActReplaceRemove.__init__(self)

        # Spinbox
        self.font_size_entry = tk.Spinbox(
            self.font_toolbar, width=2, justify='center', from_=0, to=99, command=self.tk_text.set_font,
            textvariable=self.tk_text.size_var, font=lr_vars.DefaultFont,
        )
        self.font_size_entry.bind("<KeyRelease-Return>", self.tk_text.set_font)

        # Spinbox
        cmd3 = lambda *a: self.tk_text.set_tegs(parent=self, remove=False)
        self.selection_font_size_entry = tk.Spinbox(
            self.font_toolbar, width=2, justify='center', from_=0, to=99, textvariable=self.size_var,
            font=lr_vars.DefaultFont, command=cmd3,
        )
        self.selection_font_size_entry.bind("<KeyRelease-Return>", cmd3)

        # Checkbutton
        self.bold_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' bold'),
            variable=self.tk_text.weight_var, command=self.tk_text.set_font,
        )

        # Checkbutton
        self.slant_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' italic'),
            variable=self.tk_text.slant_var, command=self.tk_text.set_font,
        )

        # Checkbutton
        self.underline_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' underline'),
            variable=self.tk_text.underline_var, command=self.tk_text.set_font,
        )

        # Checkbutton
        self.overstrike_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' overstrike'),
            variable=self.tk_text.overstrike_var, command=self.tk_text.set_font,
        )

        # Checkbutton
        self.selection_bold_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' bold'),
            variable=self.weight_var, command=self.bold_selection_set,
        )

        # Checkbutton
        self.selection_slant_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' italic'),
            variable=self.slant_var, command=self.bold_selection_set,
        )

        # Checkbutton
        self.selection_underline_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' underline'),
            variable=self.underline_var, command=self.bold_selection_set,
        )

        # Checkbutton
        self.selection_overstrike_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=(lr_vars.DefaultFont + ' overstrike'),
            variable=self.overstrike_var, command=self.bold_selection_set,
        )

        # Combobox
        self.font_combo = ttk.Combobox(
            self.font_toolbar, textvariable=self.tk_text.font_var, justify='center', font=lr_vars.DefaultFont,
        )
        self.font_combo['values'] = list(sorted(tk.font.families()))
        self.font_combo.bind("<KeyRelease-Return>", self.tk_text.set_font)
        self.font_combo.bind("<<ComboboxSelected>>", self.tk_text.set_font)

        # Combobox
        self.selection_font_combo = ttk.Combobox(
            self.font_toolbar, textvariable=self.font_var, justify='center', font=lr_vars.DefaultFont,
        )
        self.selection_font_combo['values'] = list(sorted(tk.font.families()))
        self.selection_font_combo.bind("<KeyRelease-Return>", self.bold_selection_set)
        self.selection_font_combo.bind("<<ComboboxSelected>>", self.bold_selection_set)

        #
        self.tk_text.set_font()
        self.bold_selection_set()

        # Combobox background color
        self.background_color_combo = ttk.Combobox(
            self.cbx_bar, textvariable=self.background_var, justify='center', font=lr_vars.DefaultFont,
        )
        self.background_color_combo['values'] = sorted(lr_lib.etc.help.COLORS.keys())

        def cmd0(*a, t=(self.tk_text, )) -> None:
            """
            obs - только self.tk_text виджет
            """
            clr = self.background_color_combo.get()
            lr_lib.gui.etc.color_change.background_color_set(self, color=clr, obs=t, )
            return
        self.background_color_combo.bind("<KeyRelease-Return>", cmd0)

        def cmd1(*a, t=('Text', 'rame', 'bel',)) -> None:
            """
            _types - любые c подходящим type()
            """
            clr = self.background_color_combo.get()
            lr_lib.gui.etc.color_change.background_color_set(self, color=clr, _types=t)
            return
        self.background_color_combo.bind("<<ComboboxSelected>>", cmd1)

        self.config(background=self.background_color_combo.get())
        return

    def bold_selection_set(self, *a) -> None:
        """
        bold tk_text font
        """
        self.tk_text.set_tegs(parent=self)
        return
