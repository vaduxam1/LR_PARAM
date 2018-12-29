# -*- coding: UTF-8 -*-
# запуск нахождения и замены group_param

import lr_lib
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.group_param import group_param, group_param_search, session_params
from lr_lib.gui.etc.group_param.group_param_filter import param_sort, param_filter

K_FIND = 'Найти'
K_CREATE = 'Создать'
K_CANCEL = 'Отменить'


@lr_vars.T_POOL_decorator
def auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """
    group params по кнопке PARAM - по LB + по началу имени
    """
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_CANCEL],
        default_key=K_CANCEL,
        title='начало param-имен',
        is_text='\n'.join(lr_vars.Params_names),
        text_before='Будет произведен поиск param, имя которых начинается на указанные имена.',
        text_after='При необходимости - добавить/удалить',
        parent=action,
    )
    ans = y.ask()
    if ans == K_FIND:
        # поиск по LB=
        params = set(session_params(action))

        # поиск по началу имени
        param_parts = set(filter(str.strip, y.text.split('\n')))
        for part in param_parts:
            ps = group_param_search(action, part)
            params.update(ps)
            continue

        params = set(param_filter(params))

        # поиск по началу имени - взять n первых символов для повторного поиска param по началу имени
        param_spin = lr_vars.SecondaryParamLen.get()
        if param_spin:
            for p in params.copy():  # params.update
                part = p[:param_spin]
                ap = group_param_search(action, part)
                params.update(ap)
                continue

        params = param_sort(params)
        lp = len(params)

        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_CREATE, K_CANCEL],
            default_key=K_CANCEL,
            title='Имена param',
            is_text='\n'.join(params),
            text_before='создание + автозамена. {} шт'.format(lp),
            text_after='При необходимости - добавить/удалить',
            parent=action,
        )
        ans = y.ask()

        # создание переданных param
        if ans == K_CREATE:
            params = y.text.split('\n')
            params = param_sort(params, deny_param_filter=False)
            # создание
            group_param(None, widget=action.tk_text, params=params, ask=False)
    return
