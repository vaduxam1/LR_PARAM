# -*- coding: UTF-8 -*-
# проверка LB RB (5) полей, на корректность


import lr_lib
import lr_lib.core.var.vars as lr_vars


def check_bound_lb_rb(left: 'id="', right: '",') -> bool:
    """id="zkau_11","""
    i = (check_bound_rb(right) and check_bound_lb(left))
    return i


def check_bound_rb(right: '",', rb_allow=lr_vars.allow_symbols.__contains__) -> bool:
    """id="zkau_11","""
    i = (right and rb_allow(right[0]))
    return i


def check_bound_lb(left: 'id="', lb_allow=lr_vars.allow_symbols.__contains__) -> bool:
    """id="zkau_11","""
    i = (left and lb_allow(left[-1]) or check_lb_percent(left) or check_lb_tnrvf(left))
    return i


def check_lb_percent(left: '%22', lb_allow=lr_lib.etc.help.HEX.__contains__) -> bool:
    """%22zkau_11","""
    i = (len(left) > 2) and lb_allow(left[-3:])
    return i


def check_lb_tnrvf(left: '\\r\\n', lb_allow=lr_vars.tnrvf.__contains__) -> bool:
    """\\r\\nzkau_11", - "\n" как два символа"""
    i = (len(left) > 1) and lb_allow(left[-2:])
    return i
