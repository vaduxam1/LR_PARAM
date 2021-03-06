﻿# -*- coding: UTF-8 -*-
# окно настройки

import inspect
import json
import tkinter as tk
import tkinter.ttk as ttk
from collections import OrderedDict
from typing import Iterable, List

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars_param
import lr_lib.core.wrsp.param
import lr_lib.core_gui.rename
import lr_lib.gui.widj.tooltip


MaxTableRows = 35


class Setting(tk.Toplevel):
    """
    настройка var
    """

    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow', ):
        super().__init__(padx=0, pady=0)
        self.parent = parent
        self.transient(self.parent)
        self.resizable(width=False, height=False)
        self.title('настройка var')
        self.buttons = {}

        self.init()
        return

    def init(self, max_row=MaxTableRows, font='Arial 7') -> None:
        """
        создание
        """
        col = 0
        modules = [
            lr_vars,
            lr_lib.core.var.vars_highlight,
            lr_lib.core.wrsp.param,
            lr_lib.core.var.vars_param,
        ]

        for module in modules:
            _source = inspect.getsource(module)
            source = _source.split('\n')
            source = map(str.strip, source)
            source = list(filter(bool, source))

            col += 1
            row = 0
            self.buttons[col] = {}
            # Label
            name = module.__name__
            lab = tk.Label(self, text=name, font='Arial 10 bold', )
            lab.grid(row=0, column=col, sticky=tk.NSEW)

            dt = module.__dict__
            attrs = sorted(attr_filter(dt), key=str.lower)

            for (num, attr) in enumerate(attrs, start=1):
                val = dt[attr]

                row += 1
                if row > max_row:
                    row = 1
                    col += 1
                    self.buttons[col] = {}
                    # Label
                    lab = tk.Label(self, text=module.__name__, )
                    lab.grid(row=0, column=col, sticky=tk.NSEW)

                try:  # len
                    lenv = len(val)
                except Exception as ex:
                    lenv = None
                ln = (' {}'.format(lenv) if (lenv is not None) else '')
                t = val.__class__.__name__
                btxt = '{num}) {at} : {t}{ln}'.format(num=num, t=t, at=attr, ln=ln, )

                # Button
                cmd = lambda dt=dt, at=attr: _var_editor(self, dt, at, )  # cmd
                apply_btn = tk.Button(self, font=font, text=btxt, command=cmd, anchor="w")
                apply_btn.grid(row=row, column=col, sticky=tk.NSEW)

                var_source = _get_source_var_comment(source, attr)
                lr_lib.gui.widj.tooltip.createToolTip(apply_btn, var_source)

                self.buttons[col][row] = apply_btn
                continue
            continue

        lr_lib.gui.etc.gui_other.center_widget(self)
        return


def _get_source_var_comment(source: List[str], attr: str, cmnt='#') -> str:
    """
    подсказки к кнопкам насройки vars из каментов исходного кода
    """
    vs = '{} ='.format(attr)
    _vs = [v for v in source if v.startswith(vs)]
    try:
        vs1 = _vs[0]
    except IndexError:
        return ''

    ind = source.index(vs1)
    vs0 = source[ind - 1]  # + пред строка
    if vs0.startswith(cmnt):
        vs0 = (vs0 + '\n')
    else:
        vs0 = ''

    if cmnt in vs1:
        vs1 = vs1.split(cmnt, 1)
        vs1 = vs1[1]
    else:
        vs1 = ''

    var_source = (vs0 + vs1).strip()

    if not var_source:  # искать до первого #
        for line in source[ind:]:
            if cmnt in line:
                ls = line.split(cmnt, 1)
                lls = len(ls)
                if lls == 2:
                    var_source = ls[1]
                else:
                    var_source = '?'
                break
            continue

    return var_source


TkVars = (tk.IntVar, tk.StringVar, tk.BooleanVar,)  # tk. типы переменных для вывода
AllowTypes = [str, int, float, tuple, list, set, dict, OrderedDict, ]  # любые типы переменных для вывода
AllowTypes.extend(TkVars)  # типы переменных для вывода


def attr_filter(dt: dict, allow_types=tuple(AllowTypes)) -> Iterable[str]:
    """
    исключить ненужные атрибуты
    """
    for attr in dt:
        da = dt[attr]
        la = len(attr)
        if (la > 1) and (not attr.startswith('__')) and isinstance(da, allow_types) and (not callable(da)):
            yield attr
        continue
    return


def to_json(var, _var: 'repr') -> str:
    """
    преобразовать var в json-str
    """
    try:
        txt = json.dumps(var, ensure_ascii=False, indent=2)
    except Exception as ex:  # TypeError: Object of type set is not JSON serializable
        txt = _var
    return txt


def _var_editor(parent, var_dict: dict, var_name: str) -> None:
    """
    Toplevel tk.Text + scroll_XY
    """
    # Toplevel
    top_level = tk.Toplevel(parent)
    top_level.attributes('-topmost', True)
    top_level.grid_columnconfigure(0, weight=1)
    top_level.grid_rowconfigure(0, weight=1)

    var = var_dict[var_name]
    typev = type(var)
    try:
        lenv = len(var)
    except Exception as ex:  # TypeError: object of type 'IntVar' has no len()
        lenv = None

    t = '{var_name} | type({typev}) | len({lenv})'
    title = t.format(typev=typev, lenv=lenv, var_name=var_name, )
    top_level.title(title)

    # Text
    tk_text = tk.Text(
        top_level, foreground='grey', background=lr_lib.core.var.vars_highlight.Background, wrap=tk.NONE,
        padx=0, pady=0, undo=True,
    )

    # var_default
    if isinstance(var, TkVars):
        var_default = var.get()
        var_default = repr(var_default)
    else:
        var_default = repr(var)

    # tk_text.insert
    txt = to_json(var, var_default)
    tk_text.insert(tk.END, txt)

    # Scrollbar
    text_scrolly = ttk.Scrollbar(top_level, orient=tk.VERTICAL, command=tk_text.yview)
    text_scrollx = ttk.Scrollbar(top_level, orient=tk.HORIZONTAL, command=tk_text.xview)
    tk_text.configure(yscrollcommand=text_scrolly.set, xscrollcommand=text_scrollx.set, bd=0, padx=0, pady=0,)

    # grid
    tk_text.grid(row=0, column=0, sticky=tk.NSEW)
    text_scrolly.grid(row=0, column=1, sticky=tk.NSEW)
    text_scrollx.grid(row=1, column=0, sticky=tk.NSEW)

    # Menu
    menubar = tk.Menu()
    top_level.config(menu=menubar)
    filemenu = tk.Menu(top_level, tearoff=0)
    menubar.add_cascade(label="reset/save", menu=filemenu)

    def _save(value_txt: str) -> None:
        """пересохранить var"""
        value = eval(value_txt)
        if isinstance(var, TkVars):
            var_dict[var_name].set(value)
        else:
            var_dict[var_name] = value
        return

    def var_save() -> None:
        """сохранить изменения в var"""
        txt = tk_text.get(1.0, tk.END)
        _save(txt)
        return

    def var_reset() -> None:
        """сбросить изменения в tk.Text и var"""
        tk_text.delete(1.0, tk.END)
        txt = to_json(var, var_default)
        tk_text.insert(tk.END, txt)
        _save(txt)
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
