# -*- coding: UTF-8 -*-
# нахождение param, в файлах ответов split
import re
import tkinter as tk

import lr_lib
import lr_lib.core_gui.group_param.gp_job
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_start
import lr_lib.core_gui.group_param.gp_filter
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP, CREATE_or_FIND


def group_param_search_by_split(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source,
        wrsp_create=False,
        action_text=True,
        ask=True,
        ask2=True,
) -> list:
    """
    поиск param в RequestBody/RequestHeader файлах
    """
    params = set()
    param_texts = lr_lib.core_gui.group_param.gp_job._text_from_params_source(params_source)

    for (file, text_) in param_texts:
        for text in text_.split('\n'):
            st = text.split('=')
            for sa in st[1:]:
                ps = sa.split('&')
                pa = ps[0]

                if '%' in pa:
                    pp = pa.split('%22')
                else:
                    pp = [pa]
                for pm in pp:
                    if any(a in pm for a in ' %'):
                        continue

                    param = pm.replace('"', '').strip()
                    params.add(param)  # добавить
                    continue
                continue
            continue
        continue

    if action_text and (not isinstance(action_text, str)):
        action_text = action.web_action._all_web_body_text()
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, action_text=action_text)

    if ask2:
        cf = CREATE_or_FIND(wrsp_create)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [cf, K_SKIP],
            default_key=cf,
            title='Поиск param в RequestBody/RequestHeader файлах.',
            is_text='\n'.join(params),
            text_before='Поиск param в RequestBody/RequestHeader файлах, каталога "data".\n'
                        'После поиска, необходимо удалить "лишнее", '
                        'то что не является param.\n\nнайдено {} шт'.format(len(params)),
            text_after='добавить/удалить',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()

        # создание param
        if ans == cf:
            params = y.text.split('\n')
            params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
        else:
            return []

    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return params
