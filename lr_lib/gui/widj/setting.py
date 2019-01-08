# -*- coding: UTF-8 -*-
# окно настройки

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core.var.vars_other
import lr_lib.core.var.vars_highlight
import lr_lib.core_gui.rename


class Setting(tk.Toplevel):
    """настройка var"""
    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow'):
        super().__init__(padx=0, pady=0)
        self.parent = parent
        self.transient(self.parent)
        self.resizable(width=False, height=False)
        self.title('настройка var')

        dt_param = lr_lib.core.var.vars_param.__dict__
        dt_color = lr_lib.core.var.vars_highlight.__dict__
        dt_vars = lr_vars.__dict__

        #
        vv1 = [
            v for v in dt_param if (
                    (not v.startswith('__'))
                    and isinstance(dt_param[v], (str, tuple, list, set, dict))
                    and (len(v) > 1))
               ]
        for (e, v) in enumerate(vv1, start=1):
            apply_btn = tk.Button(
                self, font='Arial 8 bold', text=v, command=lambda v=v: _set_transacts(self, dt_param, v, ),
            )
            apply_btn.grid(row=e, column=1, sticky=tk.NSEW)
            continue

        #
        vv1 = [
            v for v in dt_vars if (
                    (not v.startswith('__'))
                    and isinstance(dt_vars[v], (str, tuple, list, set, dict))
                    and (len(v) > 1))
        ]
        for (e, v) in enumerate(vv1, start=1):
            apply_btn = tk.Button(
                self, font='Arial 8 bold', text=v, command=lambda v=v: _set_transacts(self, dt_vars, v, ),
            )
            apply_btn.grid(row=e, column=2, sticky=tk.NSEW)
            continue

        #
        vv1 = [
            v for v in dt_color if (
                    (not v.startswith('__'))
                    and isinstance(dt_color[v], (str, tuple, list, set, dict))
                    and (len(v) > 1))
        ]
        for (e, v) in enumerate(vv1, start=1):
            apply_btn = tk.Button(
                self, font='Arial 8 bold', text=v, command=lambda v=v: _set_transacts(self, dt_color, v, ),
            )
            apply_btn.grid(row=e, column=3, sticky=tk.NSEW)
            continue

        lr_lib.gui.etc.gui_other.center_widget(self)
        return


def _set_transacts(parent, var_dict, var_name, ) -> None:
    """Toplevel tk.Text + scroll_XY"""
    var = var_dict[var_name]

    top_level = tk.Toplevel(parent)
    top_level.attributes('-topmost', True)
    title = 'type({tp}) | len({ln})'.format(tp=type(var), ln=len(var), )
    top_level.title(title)

    top_level.grid_columnconfigure(0, weight=1)
    top_level.grid_rowconfigure(0, weight=1)

    menubar = tk.Menu()
    top_level.config(menu=menubar)
    filemenu = tk.Menu(top_level, tearoff=0)
    menubar.add_cascade(label="reset/save", menu=filemenu)

    tk_text = tk.Text(
        top_level, foreground='grey', background=lr_lib.core.var.vars_highlight.Background, wrap=tk.NONE,
        padx=0, pady=0, undo=True,
    )

    text_scrolly = ttk.Scrollbar(top_level, orient=tk.VERTICAL, command=tk_text.yview)
    text_scrollx = ttk.Scrollbar(top_level, orient=tk.HORIZONTAL, command=tk_text.xview)
    tk_text.configure(
        yscrollcommand=text_scrolly.set, xscrollcommand=text_scrollx.set, bd=0, padx=0, pady=0,
    )

    _var = str(var)
    tk_text.insert(tk.END, _var)

    tk_text.grid(row=0, column=0, sticky=tk.NSEW)
    text_scrolly.grid(row=0, column=1, sticky=tk.NSEW)
    text_scrollx.grid(row=1, column=0, sticky=tk.NSEW)

    def var_save() -> None:
        """сохранить изменения в var"""
        txt = tk_text.get(1.0, tk.END)
        et = eval(txt)
        var_dict[var_name] = et
        return

    def var_reset() -> None:
        """сбросить изменения в tk.Text"""
        tk_text.delete(1.0, tk.END)
        tk_text.insert(tk.END, _var)
        et = eval(_var)
        var_dict[var_name] = et
        return

    filemenu.add_command(
        label="reset",
        command=var_reset,
    )
    filemenu.add_command(
        label="save",
        command=var_save,
    )

    return

