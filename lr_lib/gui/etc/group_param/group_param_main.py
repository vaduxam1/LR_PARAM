# -*- coding: UTF-8 -*-
# запуск нахождения и замены group_param

import lr_lib
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.group_param import group_param, group_param_search, session_params


@lr_vars.T_POOL_decorator
def auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """
    group params по кнопке PARAM - по LB + по началу имени
    """
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        ['Найти', 'Отменить'],
        is_text='\n'.join(lr_vars.Params_names),
        text_before='Будет произведен поиск param, имя которых начинается на указанные имена.',
        text_after='При необходимости - добавить/удалить',
        title='начало param-имен',
        parent=action,
    )
    ans = y.ask()
    if ans == 'Найти':
        param_parts = list(filter(bool, map(str.strip, y.text.split('\n'))))

        params = set(session_params(action))  # поиск по LB=
        for part in param_parts:
            for param in group_param_search(action, part):
                params.add(param)  # поиск по началу имени
                continue
            continue

        params = set(param_filter(params))
        param_spin = lr_vars.SecondaryParamLen.get()
        if param_spin:  # взять n первых символов для повторного поиска param по началу имени
            for p in list(filter(bool, params)):
                part = p[:param_spin]
                ap = group_param_search(action, part)
                if ap:
                    params.update(ap)
                continue

        params = param_sort(params)

        y = lr_lib.gui.widj.dialog.YesNoCancel(
            ['Создать', 'Отменить'],
            is_text='\n'.join(params),
            text_before='создание + автозамена. {} шт'.format(len(params)),
            text_after='При необходимости - добавить/удалить',
            title='Имена param',
            parent=action,
        )
        ans = y.ask()
        if ans == 'Создать':
            params = list(filter(bool, map(str.strip, y.text.split('\n'))))
            params = param_sort(params)
            group_param(None, widget=action.tk_text, params=params, ask=False)
    return


def param_sort(params: [str, ], reverse=True, ) -> [str, ]:
    """
    отсортировать param по длине, тк если имеются похожие имена, лучше сначала заменять самые длинные,
    тк иначе например заменяя "zkau_1" - можно ошибочно заменить и для "zkau_11"
    """
    pp = param_filter(params)
    params = sorted(pp, key=len, reverse=reverse)
    return params


def param_filter(params: [str, ], mpl=lr_vars.MinParamLen) -> iter((str,)):
    """отфильтровать лишние param"""
    sp = set(params)
    for pm in sp:
        if pm in lr_vars.DENY_PARAMS:
            continue
        else:
            lnp = len(pm)
            if lnp > mpl:
                if pm[mpl].isupper() and pm.startswith('on'):
                    continue  # "onScreen"

                yield pm
        continue
    return
