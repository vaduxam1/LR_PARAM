# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, на основе регулярных выражений

import re

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_job
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP, CREATE_or_FIND


def group_param_search_by_act_re(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source,
        wrsp_create=False,
        action_text=True,
        ask=True,
        ask2=True,
) -> [str, ]:
    """
    group params поиск, на основе регулярных выражений
    """
    if ask:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_SKIP],
            title='3.1) запрос: action.c regexp',
            is_text='\n'.join(lr_lib.core.var.vars_param.REGEXP_PARAMS),
            text_before='3) Поиск param в [ ACTION.C ] тексте:\n\n'
                        'Поиск re.findall(regexp, text) слов в тексте, '
                        'например zkau_12 для "value=zkau_12".',
            text_after='добавить/удалить',
            parent=action,
        )
        ans = y.ask()
        if ans == K_FIND:
            regexps = y.text.split('\n')
            regexps = map(str.strip, regexps)
            regexps = filter(bool, regexps)
        else:
            return []
    else:
        regexps = lr_lib.core.var.vars_param.REGEXP_PARAMS

    params = []
    for rx in regexps:
        prs = group_param_search_quotes(params_source, regexp=rx)
        prs = lr_lib.core_gui.group_param.gp_filter._param_filter(prs)
        params.extend(prs)
        continue

    if action_text and (not isinstance(action_text, str)):
        action_text = action.web_action._all_web_body_text()
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, action_text=action_text)

    if not params:
        return []

    if ask2:
        cf = CREATE_or_FIND(wrsp_create)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [cf, K_SKIP],
            title='3.2) ответ',
            is_text='\n'.join(params),
            text_before='3) найдено {} шт'.format(len(params)),
            text_after='добавить/удалить',
            parent=action,
            default_key=cf,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()
        if ans != cf:
            return []
        params = y.text.split('\n')
        params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)

    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return params


Filter = lr_lib.core.var.vars_param.param_valid_letters.__contains__  # фильтр поиск param
RegExp = r'=(.+?)\"'  # re.findall по умолчанию


def group_param_search_quotes(params_source, regexp=RegExp, ) -> iter((str,)):
    """
    фильтр поиск param, внутри кавычек
    """
    params = _get_params(params_source, regexp=regexp)
    params = filter(str.strip, params)
    for param in params:
        if all(map(Filter, param)):
            yield param  # не содержит неподходящих символов
        continue
    return


def _get_params(params_source, regexp=RegExp, ) -> iter((str,)):
    """
    поиск param, внутри кавычек
    """
    act_text_ = lr_lib.core_gui.group_param.gp_job._text_from_params_source(params_source)
    for (name, text) in act_text_:
        params = re.findall(regexp, text)
        yield from params
        continue
    return
