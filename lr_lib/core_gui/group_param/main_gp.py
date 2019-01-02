# -*- coding: UTF-8 -*-
# запуск нахождения и замены group_param

import lr_lib
import lr_lib.core.var.vars_other
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_lb
import lr_lib.core_gui.group_param.gp_act_re
import lr_lib.core_gui.group_param.gp_act_startswith
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_response_re
from lr_lib.core_gui.group_param.gp_var import K_CREATE, K_CANCEL


@lr_lib.core.var.vars_other.T_POOL_decorator
def auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """
    group params по кнопке PARAM - по LB + по началу имени
    """
    params = set()

    # поиск по началу имени, в action.c
    ps = lr_lib.core_gui.group_param.gp_act_startswith.group_param_search_by_name(action)
    params.update(ps)

    if (not ps) and isinstance(ps, set):
        return

    # поиск по LB=, в action.c
    prs = lr_lib.core_gui.group_param.gp_act_lb.group_param_search_by_lb(action)
    params.update(prs)

    # поиск по LB, в action.c, на основе регулярных выражений
    prr = lr_lib.core_gui.group_param.gp_act_re.group_param_search_by_act_re(action)
    params.update(prr)

    # поиск param, в файлах ответов
    psr = lr_lib.core_gui.group_param.gp_response_re.group_param_search_by_resp_re(action)
    params.update(psr)

    # поиск(в action.c) по началу имени - взять n первых символов - запускать последним!
    pre = lr_lib.core_gui.group_param.gp_act_startswith.group_param_search_by_exist_param(action, params)
    params.update(pre)

    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params)
    lp = len(params)

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_CREATE, K_CANCEL],
        default_key=K_CANCEL,
        title='Финальное окно',
        is_text='\n'.join(params),
        text_before='создание WRSP и автозамена в action.c : WRSP = {} шт'.format(lp),
        text_after='добавить/удалить',
        parent=action,
        color='Orange'
    )
    ans = y.ask()

    # создание переданных param
    if ans == K_CREATE:
        params = y.text.split('\n')
        params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
        # создание
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return
