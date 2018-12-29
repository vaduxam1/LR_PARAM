# -*- coding: UTF-8 -*-
# нахождение и замена group_param, на основе регулярных выражений

import re

import lr_lib
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.group_param import group_param
from lr_lib.gui.etc.group_param.group_param_filter import param_sort, param_filter

K_FIND = 'Найти'
K_CREATE = 'Создать'
K_CANCEL = 'Отменить'


def _param_filter(params: [str, ], min_param_len=lr_vars.MinParamLen,
                  deny=lr_vars.DENY_Startswitch_PARAMS, ) -> [str, ]:
    """удалить не param-слова"""
    params = param_filter(params)
    for param in params:
        if len(param) < min_param_len:
            continue

        check = True
        for dp in deny:
            if param.startswith(dp):  # "uuid_1" - "статичный" параметр, не требующий парамертизации
                ps = param.split(dp, 2)
                lps = len(ps)
                if lps == 2:
                    p1 = ps[1]
                    numeric = map(str.isnumeric, p1)
                    check = (not all(numeric))
                elif lps < 2:
                    check = False
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
        [K_FIND, K_CANCEL],
        title='regexp {} шт.'.format(len(lr_vars.REGEXP_PARAMS)),
        is_text='\n'.join(lr_vars.REGEXP_PARAMS),
        text_before='Будет произведен поиск param: re.findall(regexp, action_text)',
        text_after='При необходимости - добавить/удалить',
        parent=action,
    )
    ans = y.ask()
    if ans == K_FIND:
        yt = y.text.split('\n')
        regexps = param_filter(map(str.strip, yt))
    else:
        return

    params = []
    for rx in regexps:
        prs = group_param_search_quotes(action, regexp=rx)
        prs = _param_filter(prs)
        params.extend(prs)
        continue

    params = param_sort(params)
    if params:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_CREATE, K_CANCEL],
            title='param {} шт.'.format(len(params)),
            is_text='\n'.join(params),
            text_before='Будет произведено создание param',
            text_after='При необходимости - добавить/удалить',
            parent=action,
        )
        ans = y.ask()
        if ans == K_CREATE:
            params = y.text.split('\n')
            params = param_sort(params, deny_param_filter=False)
            group_param(None, widget=action.tk_text, params=params, ask=False)
    return


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
