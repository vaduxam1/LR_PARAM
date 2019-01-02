# -*- coding: UTF-8 -*-
# фильтрация и сортировка param
import lr_lib.core
import lr_lib.core.var.vars_param
from lr_lib.core.var import vars as lr_vars


def param_sort(params: [str, ], reverse=True, _filter=True, deny_param_filter=True, ) -> [str, ]:
    """
    отсортировать param по длине, тк если имеются похожие имена, лучше сначала заменять самые длинные,
    тк иначе например заменяя "zkau_1" - можно ошибочно заменить и для "zkau_11"
    """
    if _filter:
        params = param_filter(params, deny_param_filter=deny_param_filter, )
    params = sorted(params, key=len, reverse=reverse)
    return params


def param_filter(params: [str, ], len_p_min=lr_vars.MinParamLen, deny=lr_lib.core.var.vars_param.DENY_PARAMS,
                 deny_param_filter=True, ) -> iter((str,)):
    """отфильтровать лишние param"""
    params = set(filter(str.strip, params))  # отфильтровать bool и только whitespace str

    if deny_param_filter:
        for param in params:
            if param in deny:
                continue
            else:
                len_p = len(param)
                if len_p > len_p_min:  # иногда находит чтото 1-2 символьное, но явно param должен быть min=3 символа
                    if filter_deny_onUpper(param):
                        continue  # "onScreen"
                    # иначе это param - вернуть
                    yield param
            continue
    else:  # иначе это param? - "onScreen_123-onScreen_asd" - вернуть?
        yield from params
    return


def filter_deny_onUpper(param: str, n=2, s='on', ) -> bool:
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


def _param_filter(params: [str, ], min_param_len=lr_vars.MinParamLen,
                  deny=lr_lib.core.var.vars_param.DENY_Startswitch_PARAMS, ) -> [str, ]:
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
