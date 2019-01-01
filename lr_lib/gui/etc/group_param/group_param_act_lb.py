# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, по символам(LB) слева от param
import re
import tkinter as tk

import lr_lib
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.group_param_filter import param_sort
from lr_lib.gui.etc.group_param.group_param_part import _group_param_search

K_FIND = 'Найти'
K_SKIP = 'Пропуск'


def session_params(action: 'lr_lib.gui.action.main_action.ActionWindow', lb_list=None, ask=True, ) -> list:
    """поиск param в action, по LB="""
    if lb_list is None:
        lb_list = lr_vars.LB_PARAM_FIND_LIST

    if ask:
        text = action.tk_text.get(1.0, tk.END)

        # что за param?
        lb_uuid = re.findall(r'uuid_\d=', text)
        lb_col_count = re.findall(r'p_p_col_count=\d&', text)

        ts = set(lb_list + lb_uuid + lb_col_count)
        text = '\n'.join(ts)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[K_FIND, K_SKIP],
            default_key=K_FIND,
            title='поиск param в action, используя action-LB',
            is_text=text,
            text_before='Найти param в action.c, используя action-LB - символы слева от param, в action.c тексте.',
            text_after='добавить/удалить action-LB, с новой строки',
            parent=action,
        )
        if y.ask() == K_FIND:
            lb_list = y.text.split('\n')
        else:
            return []

    params = []
    for lb_in_action in filter(str.strip, lb_list):
        ps = _group_param_search(action, lb_in_action, part_mode=False)
        params.extend(ps)
        continue

    params = param_sort(params)

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_SKIP],
        default_key=K_FIND,
        title='Имена param',
        is_text='\n'.join(params),
        text_before='найдено {} шт'.format(len(params)),
        text_after='добавить/удалить',
        parent=action,
        color=lr_vars.PopUpWindColor1,
    )
    ans = y.ask()

    # создание param
    if ans == K_FIND:
        params = y.text.split('\n')
    else:
        return []

    params = param_sort(params)
    return params