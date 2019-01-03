# -*- coding: UTF-8 -*-
# нахождение param, в файлах ответов split
import re
import tkinter as tk

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_startswith
import lr_lib.core_gui.group_param.gp_filter
from lr_lib.core_gui.group_param.gp_var import K_FIND, K_SKIP, responce_files_texts


def group_param_search_by_split(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        wrsp_create=False,
) -> list:
    """
    поиск param в RequestBody/RequestHeader файлах
    """
    params = set()

    for (file, text_) in responce_files_texts():
        if 'Request' not in file:
            continue

        for text in text_.split('\n'):
            st = text.split('=')
            for s in st[1:]:
                ps = s.split('&')
                p = ps[0]

                if '%' in p:
                    pp = p.split('%22')
                else:
                    pp = [p]

                for pm in pp:
                    if any(a in pm for a in ' %'):
                        continue
                    pm = pm.replace('"', '')
                    params.add(pm)
                    continue

                continue
            continue
        continue

    params = map(str.strip, params)
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params)

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_SKIP],
        default_key=K_FIND,
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
    if ans == K_FIND:
        params = y.text.split('\n')
    else:
        return []

    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return params
