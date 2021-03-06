﻿# -*- coding: UTF-8 -*-
# фильтрация и сортировка param

import string
from typing import Iterable, List, Set

import lr_lib.core
from lr_lib.core.var import vars as lr_vars
import lr_lib.core.var.vars_param as vars_param


def param_sort(
        params: Iterable[str],
        reverse=True,
        _filter=True,
        deny_param_filter=True,
        action_text=None
) -> List[str]:
    """
    отсортировать param по длине, тк если имеются похожие имена, лучше сначала заменять самые длинные,
    тк иначе например заменяя "zkau_1" - можно ошибочно заменить и для "zkau_11"
    """
    if _filter:
        params = param_filter(params, deny_param_filter=deny_param_filter, )
        if deny_param_filter:
            params = _param_filter(params)

    if action_text:
        params = only_in_action_param_filter(params)

    params = sorted(params, key=len, reverse=reverse)
    return params


_PFDeny_1 = ('-' + string.ascii_lowercase)  # не {param} слова "-321" или "t11"


def param_filter(params: List[str], deny_param_filter=True, action=None) -> Iterable[str]:
    """
    отфильтровать лишние param
    """
    params = filter(str.strip, params)
    params = set(params)
    if not deny_param_filter:
        yield from params
        return

    deny_numeric = (not lr_vars.AllowOnlyNumericParam.get())
    deny = vars_param.DENY_ENABLE.get()
    if not action:
        action = lr_vars.Window.get_main_action()

    for param in params:
        len_p = len(param)

        if deny:
            p_lower = param.lower()
            if any(map(param.startswith, vars_param.DENY_Force_Startswitch_PARAMS)):
                continue
            elif p_lower in vars_param.DENY_PARAMS_LOWER:
                continue
            elif any(map(param.endswith, vars_param.DENY_Force_Endswitch_PARAMS)):
                continue
            elif param in vars_param.DENY_PARAMS_EQ:
                continue
            elif any(a in p_lower for a in vars_param.DENY_Force_Contains_Lower_PARAMS):
                continue
            elif any(a in param for a in vars_param.DENY_Force_Contains_PARAMS):
                continue

        if (len_p < lr_vars.MinParamLen) or (len_p > lr_vars.MaxParamLen):
            continue
        elif not all(map(vars_param.param_valid_letters.__contains__, param)):
            continue  # "asd wer*&3"
        elif filter_deny_onUpper(param):
            continue  # "onScreen"
        elif deny_numeric and all(map(str.isnumeric, param)):
            continue  # имена только из цифр, например порт "8888"
        elif param.endswith('px') and (len_p > 2) and all(map(str.isnumeric, param[:-2])):
            continue  # "224px"
        elif param.startswith('JSESSIONID') and (len_p > 10) and all(map(str.isnumeric, param[10:])):
            continue  # "JSESSIONID2" - уже найденный LoadRunner-ом параметр
        elif any(map(param.startswith, _PFDeny_1)) and (len_p > 1) and all(map(str.isnumeric, param[1:])):
            continue  # "-310"
        elif action and (param in action.web_action.websReport.wrsp_and_param_names):
            continue  # уже найденное имя WRSP
        else:
            yield param  # иначе это param - вернуть
        continue
    return


def filter_deny_onUpper(param: str, n=2, s='on') -> bool:
    """
    находит "onScreen" - и много подобных "on"+Upper не нуждающихся в параметризации
    :param param: str: "zkau_123"
    :return: True - запретить / False - разрешить
    """
    try:
        letter = param[n]
    except IndexError:
        return False  # не onScreen разрешить, при большом n

    state = letter.isupper()
    if state:
        state = param.startswith(s)
    return state


def _param_filter(params: List[str]) -> List[str]:
    """
    удалить не param-слова
    """
    params = param_filter(params)
    _MinParamNumsOnlyLen = lr_vars.MinParamNumsOnlyLen.get()

    for param in params:
        len_p = len(param)
        if (len_p < lr_vars.MinParamLen) or (len_p > lr_vars.MaxParamLen):
            continue
        elif any(map(vars_param.param_splitters.__contains__, param)):
            continue
        elif all(map(str.isnumeric, param)) and (len_p < _MinParamNumsOnlyLen):
            continue

        check = True
        for dp in vars_param.DENY_Startswitch_PARAMS:
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


def only_in_action_param_filter(params: List[str], action_text=None) -> Iterable[str]:
    """
    удалить param которых нету в action.c
    """
    if action_text is None:
        action = lr_vars.Window.get_main_action()
        action_text = action.web_action._all_web_body_text()

    for param in params:
        is_param = lr_lib.core.etc.lbrb_checker.check_in_text_param_all_bound_lb_rb(text=action_text, param=param)
        if any(is_param):
            yield param
        continue
    return
