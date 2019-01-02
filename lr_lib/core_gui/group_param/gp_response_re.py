# -*- coding: UTF-8 -*-
# поиск param, для action.c, но в файлах ответов, на основе регулярных выражений

import re
import os
import itertools

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.etc.excepthook
import lr_lib.gui.action._other
import lr_lib.core.etc.lbrb_checker
from lr_lib.core_gui.group_param.gp_filter import param_sort
from lr_lib.core.var import vars as lr_vars
from lr_lib.core_gui.group_param.core_gp import group_param
from lr_lib.core_gui.group_param.gp_var import K_FIND, K_SKIP, responce_files_texts


def param_from_str_1(stri: str) -> (str, str):
    """" stri("'\w+.\w+.\w+','\w+',{") """
    rs = stri.split("'")
    item = (rs[1], rs[3])
    return item


def param_from_str_2(stri: str) -> (str, str):
    """" stri("dtid=\w+&") """
    rs = stri.split("=", 1)
    item = (rs[0], rs[1][:-1])
    return item


Regxp = [
    ("'\w+.\w+.\w+','\w+',{", param_from_str_1),
    ("dtid=\w+&", param_from_str_2),
    ('jsessionid=\w+"', param_from_str_2),
]
Regxp.extend(
    ('{0}\w+"'.format(r), param_from_str_2) for r in lr_lib.core.var.vars_param.LB_PARAM_FIND_LIST if ('\\' not in r)
)


def group_param_search_by_resp_re(action: 'lr_lib.gui.action.main_action.ActionWindow', wrsp_create=False):
    """поиск param, для action.c, но в файлах ответов, на основе регулярных выражений"""
    params = {}
    wa = action.web_action.get_web_all()
    action_text = '\n'.join(w.get_body() for w in wa)

    for (file, txt) in responce_files_texts():
        for (rx, cb) in Regxp:
            st = re.findall(rx, txt)
            for stri in st:
                try:  # "'zul.sel.Treecell','bJsPt4',"
                    (a, b) = cb(stri)
                    params.setdefault(a, set()).add(b)
                except Exception as ex:
                    pass
                continue
            continue
        continue

    all_p = sorted(set(itertools.chain(*params.values())))

    in_action_param_only = []
    for param in all_p:
        at = action_text.split(param)
        for n in range(1, len(at)):
            if lr_lib.core.etc.lbrb_checker.check_bound_lb_rb(at[n - 1], at[n]):
                in_action_param_only.append(param)
                break
            continue
        continue

    in_action_param_only = param_sort(in_action_param_only)

    inf = '\n'.join(str([stri, len(params[stri]), params[stri]]) for stri in sorted(params))
    inf = 'in_action_param_only/all: {}/{}\n{}'.format(len(in_action_param_only), len(all_p), inf)
    lr_vars.Logger.info(inf)

    text = '\n'.join(in_action_param_only)
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=[K_FIND, K_SKIP],
        default_key=K_FIND,
        title='4) Поиск param в тексте [ Файлов Ответов ] по param-LB/RB',
        is_text=text,
        text_before='4) Поиск param в тексте [ Файлов Ответов ]:\n\nна основе регулярных выражений, по param-LB/RB:\n\n'
                    'найдено {} шт'.format(len(in_action_param_only)),
        text_after='добавить/удалить',
        parent=action,
        color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
    )

    if y.ask() != K_FIND:
        return []

    yt = y.text.split('\n')
    in_action_param_only = param_sort(yt, deny_param_filter=False)
    if wrsp_create:  # создать wrsp
        group_param(None, in_action_param_only, widget=action.tk_text, ask=False)
    return in_action_param_only
