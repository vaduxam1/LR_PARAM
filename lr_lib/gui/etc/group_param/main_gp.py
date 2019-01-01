# -*- coding: UTF-8 -*-
# запуск нахождения и замены group_param

import lr_lib
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.core_gp import group_param
from lr_lib.gui.etc.group_param.gp_act_lb import session_params
from lr_lib.gui.etc.group_param.gp_filter import param_sort
from lr_lib.gui.etc.group_param.gp_act_startswith import group_param_search, run_in_end_param_from_param
from lr_lib.gui.etc.group_param.gp_response_re import re_r_auto_param_creator
from lr_lib.gui.etc.group_param.gp_act_re import re_auto_param_creator
from lr_lib.gui.etc.group_param.gp_var import K_CREATE, K_CANCEL


@lr_vars.T_POOL_decorator
def auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """
    group params по кнопке PARAM - по LB + по началу имени
    """
    params = set()

    # поиск по началу имени, в action.c
    ps = group_param_search(action)
    params.update(ps)

    # поиск по LB=, в action.c
    prs = session_params(action)
    params.update(prs)

    # поиск по LB, в action.c, на основе регулярных выражений
    prr = re_auto_param_creator(action, wrsp_create=False)
    params.update(prr)

    # поиск param, в файлах ответов
    psr = re_r_auto_param_creator(action)
    params.update(psr)

    # поиск(в action.c) по началу имени - взять n первых символов
    pre = run_in_end_param_from_param(action, params)
    params.update(pre)

    params = param_sort(params)
    lp = len(params)

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_CREATE, K_CANCEL],
        default_key=K_CANCEL,
        title='Имена param',
        is_text='\n'.join(params),
        text_before='создание + автозамена. {} шт'.format(lp),
        text_after='добавить/удалить',
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
