# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, по символам(LB) слева от param
import re
import os
import tkinter as tk
from typing import Iterable, Tuple, List, Callable

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_start
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_job
from lr_lib.core_gui.group_param.gp_var import responce_files_texts
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP, CREATE_or_FIND
import lr_lib.core.var.vars as lr_vars

T1 = '1.1) запрос: поиск param в action, используя action-LB'
T2 = '1) Поиск param в [ ACTION.C ] тексте: используя action-LB символы.\n' \
     'Например используя action-LB: ( value= ), для action.c файла подобного содержания:\n\n' \
     'web_url("index.zul",\n' \
     '... "value=zkau_1"; ... value=editZul_1;...\n... value={editZul_2, "zkau_2"} ...\n' \
     '... "item=zkau_3"; ... item=editZul_3; ...\n... item={editZul_4, "zkau_4"} ...\nLAST);\n\n' \
     'можно найти такие param: zkau_1, editZul_1.'
T3 = '1.2) ответ action-LB'
T4 = '1) найдено {} шт'


def group_param_search_by_lb(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source: 'str or lr_lib.gui.action.main_action.ActionWindow',
        lb_items=None,
        ask=True,
        ask2=True,
        wrsp_create=False,
        texts_for_lb=None,
        MutableLBRegs=lr_lib.core.var.vars_param.MutableLBRegs,
        action_text=True,
        t1=T1, t2=T2, t3=T3, t4=T4, **kwargs
) -> list:
    """
    поиск param в action, по LB=
    """
    is_action_text = (texts_for_lb is None)

    if is_action_text:
        texts_for_lb = [action.tk_text.get(1.0, tk.END), ]  # action.c
    elif isinstance(texts_for_lb, str):
        texts_for_lb = [texts_for_lb, ]
    else:
        texts_for_lb = (t[1] for t in responce_files_texts())

    if lb_items is None:
        lb_items = set(lr_lib.core.var.vars_param.LB_PARAM_FIND_LIST)

    if lr_lib.core.var.vars_param.disk_lb_var.get():
        f = os.path.join(lr_vars.lib_folder, lr_lib.core.var.vars_param.LFILE)
        if os.path.exists(f):
            with open(f, errors='replace') as f:
                for _lb in filter(str.strip, f):
                    lb_items.add(_lb)
                    continue

    if MutableLBRegs:
        for text in texts_for_lb:
            for r in MutableLBRegs:
                lb = re.findall(r, text)
                lb_items.update(lb)
                continue
            continue

    if ask:  # диалог окно поиск param
        lb_items = _ask_lb_items(action, lb_items, t1, t2)

    lb_items = list(filter(bool, map(str.strip, lb_items)))
    if not lb_items:
        return []

    params = lr_lib.core_gui.group_param.gp_job._group_param_search_by_lb(lb_items, params_source)
    if action_text and (not isinstance(action_text, str)):
        action_text = action.web_action._all_web_body_text()
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, action_text=action_text)

    if ask2:
        cf = CREATE_or_FIND(wrsp_create)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [cf, K_SKIP],
            default_key=cf,
            title=t3,
            is_text='\n'.join(params),
            text_before=t4.format(len(params)),
            text_after='добавить/удалить: необходимо удалить "лишнее", то что не является param',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()

        # создание param
        if ans == cf:
            params = y.text.split('\n')
        else:
            return []

        params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return params


def _ask_lb_items(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        lb_items: List[str],
        t1: str,
        t2: str,
) -> List[str]:
    """
    диалог окно поиск param
    """
    tt = '\n'.join(filter(bool, map(str.strip, lb_items)))

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=[K_FIND, K_SKIP],
        default_key=K_FIND,
        title=t1,
        is_text=tt,
        text_before=t2,
        text_after='добавить/удалить',
        parent=action,
    )

    if y.ask() == K_FIND:
        lb_items = y.text.split('\n')
    else:
        return []

    return lb_items
