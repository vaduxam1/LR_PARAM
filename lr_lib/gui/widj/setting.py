# -*- coding: UTF-8 -*-
# окно настройки

import json
import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core.var.vars_other
import lr_lib.core.var.vars_highlight
import lr_lib.core_gui.rename
import lr_lib.core.wrsp.param


class Setting(tk.Toplevel):
    """настройка var"""
    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow', max_row=15, ):
        super().__init__(padx=0, pady=0)
        self.parent = parent
        self.transient(self.parent)
        self.resizable(width=False, height=False)
        self.title('настройка var')
        self.buttons = {}

        col = 0
        modeles = [
            lr_lib.core.var.vars_param,
            lr_lib.core.var.vars_highlight,
            lr_vars,
            lr_lib.core.wrsp.param,
        ]

        for module in modeles:
            col += 1
            row = 0
            self.buttons[col] = {}

            # Label
            name = module.__name__
            lab = tk.Label(self, text=name, )
            lab.grid(row=0, column=col, sticky=tk.NSEW)

            dt = module.__dict__
            attrs = attr_filter(dt)

            for at in attrs:
                row += 1
                if row > max_row:
                    row = 1
                    col += 1
                    self.buttons[col] = {}

                    # Label
                    lab = tk.Label(self, text=module.__name__, )
                    lab.grid(row=0, column=col, sticky=tk.NSEW)

                # Button
                command = lambda dt=dt, at=at: _var_editor(self, dt, at, )
                apply_btn = tk.Button(self, font='Arial 8 bold', text=at, command=command,)
                apply_btn.grid(row=row, column=col, sticky=tk.NSEW)

                self.buttons[col][row] = apply_btn
                continue
            continue

        lr_lib.gui.etc.gui_other.center_widget(self)
        return


def attr_filter(dt: dict, allow_types=(str, tuple, list, set, dict, ), ) -> iter((str, )):
    """исключить ненужные атрибуты"""
    for attr in dt:
        da = dt[attr]
        if (not attr.startswith('__')) and isinstance(da, allow_types) and (len(attr) > 1) \
                and (not callable(da)):
            yield attr
        continue
    return


def _var_editor(parent, var_dict, var_name, ) -> None:
    """Toplevel tk.Text + scroll_XY"""
    var = var_dict[var_name]

    # Toplevel
    top_level = tk.Toplevel(parent)
    top_level.attributes('-topmost', True)
    title = 'type({tp}) | len({ln})'.format(tp=type(var), ln=len(var), )
    top_level.title(title)

    top_level.grid_columnconfigure(0, weight=1)
    top_level.grid_rowconfigure(0, weight=1)

    # Text
    tk_text = tk.Text(
        top_level, foreground='grey', background=lr_lib.core.var.vars_highlight.Background, wrap=tk.NONE,
        padx=0, pady=0, undo=True,
    )

    _var = repr(var)
    try:
        tk_text.insert(tk.END, json.dumps(var, ensure_ascii=False, indent=2))
    except Exception as ex:  # TypeError: Object of type set is not JSON serializable
        tk_text.insert(tk.END, _var)
    # Scrollbar
    text_scrolly = ttk.Scrollbar(top_level, orient=tk.VERTICAL, command=tk_text.yview)
    text_scrollx = ttk.Scrollbar(top_level, orient=tk.HORIZONTAL, command=tk_text.xview)
    tk_text.configure(
        yscrollcommand=text_scrolly.set, xscrollcommand=text_scrollx.set, bd=0, padx=0, pady=0,
    )

    # grid
    tk_text.grid(row=0, column=0, sticky=tk.NSEW)
    text_scrolly.grid(row=0, column=1, sticky=tk.NSEW)
    text_scrollx.grid(row=1, column=0, sticky=tk.NSEW)

    # Menu
    menubar = tk.Menu()
    top_level.config(menu=menubar)
    filemenu = tk.Menu(top_level, tearoff=0)
    menubar.add_cascade(label="reset/save", menu=filemenu)

    def var_save() -> None:
        """сохранить изменения в var"""
        txt = tk_text.get(1.0, tk.END)
        et = eval(txt)
        var_dict[var_name] = et
        return

    def var_reset() -> None:
        """сбросить изменения в tk.Text"""
        tk_text.delete(1.0, tk.END)
        try:
            tk_text.insert(tk.END, json.dumps(var, ensure_ascii=False, indent=2))
        except Exception as ex:  # TypeError: Object of type set is not JSON serializable
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

