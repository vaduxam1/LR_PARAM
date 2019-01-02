# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, на основе регулярных выражений

import re

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
from lr_lib.core_gui.group_param.core_gp import group_param
from lr_lib.core_gui.group_param.gp_filter import param_sort, param_filter, _param_filter
from lr_lib.core_gui.group_param.gp_var import K_FIND, K_CREATE, K_SKIP


def re_auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow', wrsp_create=False) -> [str, ]:
    """
    group params поиск, на основе регулярных выражений
    """
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_SKIP],
        title='3.1) запрос: action.c regexp',
        is_text='\n'.join(lr_lib.core.var.vars_param.REGEXP_PARAMS),
        text_before='3) Поиск param в [ ACTION.C ] тексте:\n\n'
                    'Поиск re.findall(regexp, action_text) слов в action-тексте, например zkau_12 для "value=zkau_12".',
        text_after='добавить/удалить',
        parent=action,
    )
    ans = y.ask()
    if ans == K_FIND:
        yt = y.text.split('\n')
        regexps = param_filter(map(str.strip, yt))
    else:
        return []

    params = []
    for rx in regexps:
        prs = group_param_search_quotes(action, regexp=rx)
        prs = _param_filter(prs)
        params.extend(prs)
        continue

    params = param_sort(params)

    if params:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_SKIP],
            title='3.2) ответ',
            is_text='\n'.join(params),
            text_before='3) найдено {} шт'.format(len(params)),
            text_after='добавить/удалить',
            parent=action,
            default_key=(K_SKIP if wrsp_create else K_FIND),
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()
        if ans == K_FIND:
            params = y.text.split('\n')
            params = param_sort(params, deny_param_filter=False)

            if wrsp_create:  # создать wrsp
                group_param(None, params, widget=action.tk_text, ask=False)

            return params
    return []


Filter = lr_lib.core.wrsp.param.wrsp_allow_symb.__contains__  # фильтр поиск param
RegExp = r'=(.+?)\"'  # re.findall по умолчанию


def group_param_search_quotes(action: 'lr_lib.gui.action.main_action.ActionWindow', regexp=RegExp, ) -> iter((str,)):
    """фильтр поиск param, внутри кавычек"""
    params = _get_params(action, regexp=regexp)
    params = filter(str.strip, params)
    for param in params:
        if all(map(Filter, param)):
            yield param  # не содержит неподходящих символов
        continue
    return


def _get_params(action: 'lr_lib.gui.action.main_action.ActionWindow', regexp=RegExp, ) -> iter((str,)):
    """поиск param, внутри кавычек"""
    for web_ in action.web_action.get_web_snapshot_all():
        body = web_.get_body()
        params = re.findall(regexp, body)
        yield from params
        continue
    return
