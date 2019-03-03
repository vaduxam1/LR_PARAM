# -*- coding: UTF-8 -*-
# разное

import os
from typing import Callable

import lr_lib
import lr_lib.core.var.vars as lr_vars


def get_action_file(folder: str, file='action.c') -> str:
    """
    найти action.c
    """
    if os.path.isfile(file):
        return file
    else:
        action_file = os.path.join(folder, file)
        if os.path.isfile(action_file):
            return action_file
    return ''


tta = 'pool:\n{pt}\n{pm}'.format
ttt1 = 'T/qi\n{t}\n{q_in}'.format
ttt2 = 'T={t}'.format
ttm1 = 'M/qi\n{mp}\n{q_in}'.format
ttm2 = 'M={mp}'.format
ttl = '{txt} lines[{top}:{bottom}]/{lmax} : {p}% | {v} | undo(ctrl-z)/redo(ctrl-y)'.format
restart = lr_vars.Tk.after
ver = lr_vars.VERSION


def auto_update_action_info_lab(
        self,
        config: Callable,
        tk_text: 'lr_lib.gui.widj.highlight_text.HighlightText',
        id_: int,
        timeout: int,
        check_run: Callable,
        title: Callable,
        _set_title: Callable,
) -> None:
    """
    обновление action.label с процентами и пулом
    """
    if not check_run(id_):
        return

    lines = tk_text.highlight_lines
    (top, bottom) = lines.on_sreen_line_nums
    linenum = str(tk_text.linenumbers.linenum).split(' ', 1)[0]
    p = round(int(linenum) // lines._max_line_proc)
    title(ttl(txt=_set_title(), top=top, bottom=bottom, v=ver, lmax=lines._max_line, p=p))

    try:
        pt = ttt1(q_in=lr_vars.T_POOL.pool._qsize, t=lr_vars.T_POOL._size)
    except AttributeError:  # lr_vars.T_POOL.pool._qsize0
        pt = ttt2(t=lr_vars.T_POOL._size)

    try:
        pm = ttm1(q_in=lr_vars.M_POOL.pool._qsize, mp=lr_vars.M_POOL._size)
    except AttributeError:  # lr_vars.M_POOL.pool._qsize
        pm = ttm2(mp=lr_vars.M_POOL._size)

    config(text=tta(pt=pt, pm=pm))
    tk_text.linenumbers.redraw()
    tk_text.highlight_lines.set_thread_attrs()

    # перезапуск
    restart(timeout, auto_update_action_info_lab, self, config, tk_text, id_, timeout, check_run, title, _set_title)
    return
