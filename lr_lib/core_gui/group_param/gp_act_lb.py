# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, по символам(LB) слева от param
import re
import tkinter as tk

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
from lr_lib.core.var import vars as lr_vars
from lr_lib.core_gui.group_param.gp_filter import param_sort
from lr_lib.core_gui.group_param.gp_act_startswith import _group_param_search
from lr_lib.core_gui.group_param.core_gp import group_param
from lr_lib.core_gui.group_param.gp_var import K_FIND, K_SKIP

F1 = r'uuid_\d='
F2 = r'p_p_col_count=\d&'


def session_params(action: 'lr_lib.gui.action.main_action.ActionWindow',
                   lb_list=None, ask=True, wrsp_create=False, ) -> list:
    """поиск param в action, по LB="""
    if lb_list is None:
        lb_list = lr_lib.core.var.vars_param.LB_PARAM_FIND_LIST

    if ask:
        text = action.tk_text.get(1.0, tk.END)

        # что за param?
        lb_uuid = re.findall(F1, text)
        lb_col_count = re.findall(F2, text)

        ts = set(lb_list + lb_uuid + lb_col_count)
        text = '\n'.join(ts)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[K_FIND, K_SKIP],
            default_key=K_FIND,
            title='2.1) запрос: поиск param в action, используя action-LB',
            is_text=text,
            text_before='2) Поиск param в [ ACTION.C ] тексте: используя action-LB символы.\n'
                        'Например используя action-LB: ( "value=" ), для action.c файла подобного содержания:\n\n'
                        'web_url("index.zul",\n'
                        '... "value=zkau_1"; ... value=editZul_1;...\n... value={editZul_2, "zkau_2"} ...\n'
                        '... "item=zkau_3"; ... item=editZul_3; ...\n... item={editZul_4, "zkau_4"} ...\nLAST);\n\n'
                        'можно найти такие param: zkau_1, editZul_1.',
            text_after='добавить/удалить',
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
        title='2.2) ответ',
        is_text='\n'.join(params),
        text_before='2) найдено {} шт'.format(len(params)),
        text_after='добавить/удалить',
        parent=action,
        color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
    )
    ans = y.ask()

    # создание param
    if ans == K_FIND:
        params = y.text.split('\n')
    else:
        return []

    params = param_sort(params, deny_param_filter=False)
    if wrsp_create:  # создать wrsp
        group_param(None, params, widget=action.tk_text, ask=False)
    return params
