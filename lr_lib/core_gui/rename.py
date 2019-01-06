# -*- coding: UTF-8 -*-
# переименование wrsp, и др.

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars_other
from lr_lib.core.var import vars as lr_vars

ABounds = [
    ('"LB=', '"RB='),
    ('"LB/IC=', '"RB/IC='),
]  # переименовать все wrsp, содержащие LB/RB вида

_M0 = '"'
_M1 = (' -> ' + _M0)
M = (_M0 + '{:<%s}' + _M0 + _M1 + '{}' + _M0)  # "старое имя" -> "новое имя"


@lr_lib.core.var.vars_other.T_POOL_decorator
def all_wrsp_auto_rename(gui: 'lr_lib.gui.action.main_action.ActionWindow', *args) -> None:
    """
    переименовать все wrsp, автоматически, с учетом всех настроек, для wrsp, содержащих LB/RB вида:
        ('"LB=', '"RB='), ('"LB/IC=', '"RB/IC=')
    например "JSESSIONID5" -> "P_6725_1__jsessionid__uJeCvxe"
    """
    _wrsps = tuple(gui.web_action.get_web_reg_save_param_all())
    wrsps = [w.name for w in _wrsps]
    wrsps_new = list(_lbrb_wrsps(_wrsps))

    m = max(map(len, (wrsps or [''])))
    m = (M % m)
    all_wrsps = '\n'.join(m.format(old, new) for (old, new) in zip(wrsps, wrsps_new))

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        ['Переименовать', 'Отмена'], 'Переименовать wrsp слева', 'в wrsp справа', 'wrsp',
        parent=gui, is_text=all_wrsps, )

    if y.ask() == 'Переименовать':
        with gui.block():
            _rename_wrsp(y.text, wrsps, gui)
    return


def _lbrb_wrsps(wrsps: ('lr_lib.core.action.web_.WebRegSaveParam',)) -> iter((str, )):
    """для всех wrsps, найти LR/RB из wrsp текста, и сформировать новое имя wrsp"""
    for wr in wrsps:
        lb = rb = ''

        for line in filter(bool, map(str.strip, wr.lines_list)):
            for (l_, r_) in ABounds:
                if line.startswith(l_):
                    lb = _get_bound(line, l_)
                elif line.startswith(r_):
                    rb = _get_bound(line, r_)

                if lb and rb:
                    break
                continue
            continue

        if not lb:
            lb = '_'
        if not rb:
            rb = '_'

        new_name = lr_lib.core.wrsp.param.wrsp_name_creator(wr.param, lb, rb, wr.snapshot.inf)
        yield new_name
        continue
    return


def _get_bound(line, spl, _s='",') -> str:
    """
    извлечь LR/RB из текста wrsp
    :param line: '"LB/IC=item:",'
    :param spl: '"LB/IC='
    :param _s: '",'
    :return: 'item:'
    """
    sl = line.split(spl, 1)
    ln = sl[1].rsplit(_s, 1)
    return ln[0]


def _split_rename(text: str) -> iter((str,)):
    """
    "P_6725_1__jsessionid__OLD" -> "P_6725_1__jsessionid__NEW"
    """
    for line in filter(str.strip, text.split('\n')):
        s = line.split(_M1, 1)
        s = s[1].split(_M0, 1)
        new_name = s[0].strip()
        yield new_name
        continue
    return


def _rename_wrsp(wrsps_text: str,
                 wrsps: ('lr_lib.core.action.web_.WebRegSaveParam',),
                 gui: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """автоматически переименовать все wrsp"""
    new_wrsps = list(_split_rename(wrsps_text))
    assert len(wrsps) == len(new_wrsps)

    gui.backup()
    text = gui.tk_text.get('1.0', tk.END)

    for (old, new) in zip(wrsps, new_wrsps):
        text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old),
                            lr_lib.core.wrsp.param.param_bounds_setter(new))
        text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old, start='"', end='"'),
                            lr_lib.core.wrsp.param.param_bounds_setter(new, start='"', end='"'))
        continue

    gui.web_action.set_text_list(text, websReport=True)
    gui.web_action_to_tk_text(websReport=False)
    return


@lr_lib.core.var.vars_other.T_POOL_decorator
def rename_transaction(event, parent=None, s='lr_start_transaction("', e='lr_end_transaction("') -> None:
    """
    переименование транзакции - необходимо выделять всю линию с транзакцией
    """
    selection = event.widget.selection_get().strip()
    try:
        old_name = selection.split(s, 1)[1].split('"', 1)[0]
    except IndexError:
        old_name = selection.split(e, 1)[1].split('"', 1)[0]

    if not parent:
        try:
            parent = event.widget.action
        except AttributeError as ex:
            pass

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        ['Переименовать', 'Отмена'], 'Переименовать выделенную(линию) transaction',
        'указать только новое имя transaction', 'transaction', parent=parent, is_text=old_name,
    )
    s1 = (s + old_name)
    s2 = (e + old_name)

    if y.ask() == 'Переименовать':
        new_name = y.text.strip()
        lit = event.widget.action.tk_text.get(1.0, tk.END).split('\n')
        for (e, line) in enumerate(lit):
            ln = line.lstrip()
            if ln.startswith(s1) or ln.startswith(s2):
                lit[e] = line.replace(old_name, new_name)
            continue

        event.widget.action.backup()
        event.widget.delete(1.0, tk.END)
        event.widget.insert(1.0, '\n'.join(lit))  # вставить
        event.widget.action.save_action_file(file_name=False)
    return


@lr_lib.core.var.vars_other.T_POOL_decorator
def all_wrsp_rename(gui: 'lr_lib.gui.action.main_action.ActionWindow', parent=None, ) -> None:
    """переименавать все wrsp, вручную"""
    if parent is None:
        parent = gui

    _wrsps = tuple(gui.web_action.get_web_reg_save_param_all())
    wrsps = tuple(w.name for w in _wrsps)
    mx = max(map(len, wrsps or ['']))
    m = ('"{:<%s}" -> "{}"' % mx)
    all_wrsps = '\n'.join(m.format(old, new) for (old, new) in zip(wrsps, wrsps))
    y = lr_lib.gui.widj.dialog.YesNoCancel(['Переименовать', 'Отмена'], 'Переименовать wrsp слева',
                              'в wrsp справа', 'wrsp', parent=parent, is_text=all_wrsps)

    if y.ask() == 'Переименовать':
        new_wrsps = [t.split('-> "', 1)[1].split('"', 1)[0].strip() for t in y.text.strip().split('\n')]
        assert (len(wrsps) == len(new_wrsps))
        with gui.block():
            gui.backup()
            text = gui.tk_text.get('1.0', tk.END)

            for (old, new) in zip(wrsps, new_wrsps):
                text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old),
                                    lr_lib.core.wrsp.param.param_bounds_setter(new))
                text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old, start='"', end='"'),
                                    lr_lib.core.wrsp.param.param_bounds_setter(new, start='"', end='"'))
                continue

            gui.web_action.set_text_list(text, websReport=True)
            gui.web_action_to_tk_text(websReport=False)
    return
