# -*- coding: UTF-8 -*-
# нахождение и замена group_param, на основе регулярных выражений

import re

import lr_lib
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.group_param import group_param


def _param_filter(lst: list, min_param_len=lr_vars.MinParamLen, ) -> [str, ]:
    """удалить не param-слова"""
    for param in lst:
        if len(param) < min_param_len:
            continue

        p1 = (param not in lr_vars.DENY_PARAMS)
        p2 = (param.startswith('on') and param[2].isupper())  # 'onScrean'
        check = (p1 and (not p2))

        for a in lr_vars.DENY_Startswitch_PARAMS:
            if param.startswith(a):
                ps = param.split(a, 1)
                ps = map(str.isnumeric, ps[1])

                check = (not all(ps))
                break
            continue

        if check:
            yield param
        continue
    return


@lr_vars.T_POOL_decorator
def re_auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow', ) -> None:
    """
    group params поиск, на основе регулярных выражений
    """
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        ['Найти', 'Отменить'],
        is_text='\n'.join(lr_vars.REGEXP_PARAMS),
        text_before='Будет произведен поиск param: re.findall(regexp, action_text)',
        text_after='При необходимости - добавить/удалить',
        title='regexp {} шт.'.format(len(lr_vars.REGEXP_PARAMS)),
        parent=action,
    )
    ans = y.ask()
    if ans == 'Найти':
        yt = y.text.split('\n')
        regexps = list(filter(bool, map(str.strip, yt)))
    else:
        return

    params = []
    for rx in regexps:
        prs = group_param_search_quotes(action, regexp=rx)
        prs = list(_param_filter(prs))
        params.extend(prs)
        continue

    params = list(set(params))
    if params:
        params.sort(key=lambda param: len(param), reverse=True)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            ['создать', 'Отменить'],
            is_text='\n'.join(params),
            text_before='Будет произведено создание param',
            text_after='При необходимости - добавить/удалить',
            title='param {} шт.'.format(len(params)),
            parent=action,
        )
        ans = y.ask()
        if ans == 'создать':
            params = list(filter(bool, map(str.strip, y.text.split('\n'))))
            group_param(None, widget=action.tk_text, params=params, ask=False)
    return


Filter = lr_lib.core.wrsp.param.wrsp_allow_symb.__contains__  # фильтр поиск param
RegExp = r'=(.+?)\"'  # re.findall по умолчанию


def group_param_search_quotes(action: 'lr_lib.gui.action.main_action.ActionWindow', regexp=RegExp, ) -> iter((str,)):
    """фильтр поиск param, внутри кавычек"""
    params = _get_params(action, regexp=regexp)
    for param in params:
        if all(map(Filter, param)):
            yield param  # не содержит неподходящих символов
        continue
    return


def _get_params(action: 'lr_lib.gui.action.main_action.ActionWindow', regexp=RegExp, ) -> iter((str,)):
    """поиск param, внутри кавычек"""
    for web_ in action.web_action.get_web_snapshot_all():
        params = re.findall(regexp, web_.get_body())
        params = filter(bool, map(str.strip, params))
        yield from params
        continue
    return
