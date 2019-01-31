# -*- coding: UTF-8 -*-
# проверка LB RB (5) полей, на корректность


import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param


def check_in_text_param_all_bound_lb_rb(text=None, param=None) -> iter((bool,)):
    """
    проверить корректность всех вхождений param в text
    """
    if text is None:
        action = lr_vars.Window.get_main_action()
        text = [w.get_body() for w in action.web_action.get_web_all()]
        text = '.\n.'.join(text)
    if param is None:
        param = lr_vars.VarParam.get()

    split = text.split(param)
    len_split = len(split)
    if len_split < 2:
        return ()

    for i in range(1, len_split):
        left = split[i - 1]
        right = split[i]
        check = check_bound_lb_rb(left, right)

        yield check
        continue
    return


def check_bound_lb_rb(left: 'id="', right: '",') -> bool:
    """
    id="zkau_11",
    """
    i = (check_bound_rb(right) and check_bound_lb(left))
    return i


def check_bound_rb(right: '",', rb_allow=lr_lib.core.var.vars_param.param_splitters.__contains__) -> bool:
    """
    id="zkau_11",
    """
    i = (right and rb_allow(right[0]))
    return i


def check_bound_lb(left: 'id="', lb_allow=lr_lib.core.var.vars_param.param_splitters.__contains__) -> bool:
    """
    id="zkau_11",
    """
    i = (left and lb_allow(left[-1]) or check_lb_percent(left) or check_lb_tnrvf(left))
    return i


def check_lb_percent(left: '%22', lb_allow=lr_lib.etc.help.HEX.__contains__) -> bool:
    """
    %22zkau_11",
    """
    i = (len(left) > 2) and lb_allow(left[-3:])
    return i


def check_lb_tnrvf(left: '\\r\\n', lb_allow=lr_lib.core.var.vars_highlight.tnrvf.__contains__) -> bool:
    """
    \\n\\nzkau_11"
        - "\n" как два символа '\' и 'n'
    """
    i = (len(left) > 1) and lb_allow(left[-2:])
    return i
