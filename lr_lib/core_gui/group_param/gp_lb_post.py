# -*- coding: UTF-8 -*-
# нахождение param, пост LB

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_lb
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_job
import lr_lib.core_gui.run.r_texts
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP, CREATE_or_FIND


def group_param_search_by_lb_post(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source,
        exist_params=(),
        wrsp_create=False,
        action_text=True,
        ask=True,
        ask2=True,
) -> [str, ]:
    """
    Метод основан том что, что если часть {param} имен уже известна,
    то можно извлечь, для каждого {param}, для каждого файла, каждый LB.
        Затем при помощи полученных LB, найти новые имена {param}, обычным LB-способом.
    """
    if not exist_params:
        exist_params = set(
            list(lr_lib.core.var.vars_param.Params_names) +
            list(action.web_action.websReport.wrsp_and_param_names.keys()) +
            list(action.web_action.websReport.wrsp_and_param_names.values())
        )

    lb_items = set()
    source = lr_lib.core_gui.group_param.gp_job._text_from_params_source(params_source)
    for (file, text) in source:
        for param in exist_params:
            _lb_items = lr_lib.core_gui.group_param.gp_job.all_lb_from(text, param)
            lb_items.update(_lb_items)
            continue
        continue

    if ask:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_SKIP],
            title='6.1) пост LB запрос',
            is_text='\n'.join(lb_items),
            text_before=lr_lib.core_gui.run.r_texts.TT_LBP,
            text_after='добавить/удалить',
            parent=action,
        )
        ans = y.ask()
        if ans == K_FIND:
            lb_items = set(filter(bool, y.text.split('\n')))
        else:
            return []

    params = lr_lib.core_gui.group_param.gp_act_lb.group_param_search_by_lb(
        action, params_source, lb_items=lb_items, ask=False, ask2=False, wrsp_create=False,
    )

    if action_text and (not isinstance(action_text, str)):
        action_text = action.web_action._all_web_body_text()
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, action_text=action_text)

    if not params:
        return []

    if ask2:
        cf = CREATE_or_FIND(wrsp_create)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [cf, K_SKIP],
            title='6.2) пост LB ответ',
            is_text='\n'.join(params),
            text_before='6.2) найдено {} шт'.format(len(params)),
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
