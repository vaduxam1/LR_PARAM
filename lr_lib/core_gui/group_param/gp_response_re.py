# -*- coding: UTF-8 -*-
# поиск param, для action.c, но в файлах ответов, на основе регулярных выражений

import re
import os
import itertools

import lr_lib
import lr_lib.etc.excepthook
import lr_lib.gui.action._other
import lr_lib.core.etc.lbrb_checker
from lr_lib.core_gui.group_param.gp_filter import param_sort
from lr_lib.core.var import vars as lr_vars
from lr_lib.core_gui.group_param.gp_var import K_FIND, K_SKIP


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


def re_r_auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow', encoding='utf-8', errors='replace'):
    """поиск param, для action.c, но в файлах ответов, на основе регулярных выражений"""
    params = {}
    wa = action.web_action.get_web_all()
    action_text = '\n'.join(w.get_body() for w in wa)

    fgen = os.walk(lr_vars.DEFAULT_FILES_FOLDER)
    (dirpath, dirnames, filenames) = next(fgen)
    for file in filenames:
        path = os.path.join(dirpath, file)
        try:
            with open(path, encoding=encoding, errors=errors) as f:
                txt = f.read()
        except Exception as ex:
            lr_lib.etc.excepthook.excepthook(ex)
            continue

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

    inf = '\n'.join(str([stri, len(params[stri]), params[stri]]) for stri in sorted(params))
    inf = 'in_action_param_only/all: {}/{}\n{}'.format(len(in_action_param_only), len(all_p), inf)
    lr_vars.Logger.info(inf)

    text = '\n'.join(in_action_param_only)
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=[K_FIND, K_SKIP],
        default_key=K_FIND,
        title='4) запрос/ответ: поиск param, в файлах ответов, на основе регулярных выражений, по LB/RB',
        is_text=text,
        text_before='4) поиск param, в файлах ответов: найдено {} шт'.format(len(params)),
        text_after='добавить/удалить',
        parent=action,
        color=lr_vars.PopUpWindColor1,
    )

    if y.ask() != K_FIND:
        return []

    yt = y.text.split('\n')
    in_action_param_only = param_sort(yt, deny_param_filter=False)
    return in_action_param_only
