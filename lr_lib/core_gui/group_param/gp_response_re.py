# -*- coding: UTF-8 -*-
# поиск param, по regexp и дальнейшей обработке результата

import itertools
import re

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_job
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP, CREATE_or_FIND


def param_from_str_1(stri: "'\\'zul.wnd.Window\\',\\'bJsP0\\',{'") -> (str, str):
    """"
    '\w+.\w+.\w+','\w+',{
    """
    rs = stri.split("'")  # <class 'list'>: ['', 'zul.wnd.Window', ',', 'bJsP0', ',{']
    item = (rs[1], rs[3])  # <class 'tuple'>: ('zul.wnd.Window', 'bJsP0')
    return item


def param_from_str_2(stri: "Value=bJsPk0&") -> (str, str):
    """"
    stri("dtid=\w+&")
    """
    rs = stri.split("=", 1)  # <class 'list'>: ['Value', 'bJsPk0&']
    r = rs[1][:-1]
    item = (rs[0], r)
    return item


Regxp = [
    ["'\w+.\w+.\w+','\w+", param_from_str_1],
    ["dtid=\w+&", param_from_str_2],
    ['jsessionid=\w+"', param_from_str_2],
]
Regxp.extend(
    ['{0}\w+"'.format(r), param_from_str_2] for r in lr_lib.core.var.vars_param.LB_PARAM_FIND_LIST if ('\\' not in r)
)


def group_param_search_by_resp_re(action: 'lr_lib.gui.action.main_action.ActionWindow',
                                  params_source,
                                  wrsp_create=False,
                                  action_text=True,
                                  ask=True,
                                  ask2=True,
                                  ) -> [str, ]:
    """
    поиск param, для action.c, по regexp и дальнейшей обработке результата
    """
    params = {}
    regexp = list(Regxp)

    if ask:
        text = '\n'.join(r[0] for r in regexp)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[K_FIND, K_SKIP],
            default_key=K_FIND,
            title='3.1) запрос: Поиск param по regexp с постобработкой',
            is_text=text,
            text_before='3) Поиск param в тексте {ps}:\n\nпо regexp и дальнейшей обработке результата.\n'
                        'Например в "zul.sel.Treecell" конструкциях.'.format(ps=params_source, ),
            text_after='Можно попытатся поменять regexp, но добавлять/удалять нельзя.',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )

        if y.ask() == K_FIND:
            r = list(filter(bool, map(str.strip, y.text.split('\n'))))
            regexp = [[r[n], regexp[n][1]] for n in range(len(r))]
        else:
            return []

    for (file, txt) in lr_lib.core_gui.group_param.gp_job._text_from_params_source(params_source):
        for (rx, cb) in regexp:
            st = re.findall(rx, txt)
            for stri in st:
                try:  # "'zul.sel.Treecell','bJsPt4',"
                    (a, b) = cb(stri)
                    s = params.setdefault(a, set())
                    s.add(b)
                except Exception as ex:
                    pass
                continue
            continue
        continue

    all_p = sorted(set(itertools.chain(*params.values())))

    if action_text and (not isinstance(action_text, str)):
        action_text = action.web_action._all_web_body_text()
    in_action_param_only = lr_lib.core_gui.group_param.gp_filter.param_sort(all_p, action_text=action_text)

    iapo = {k: {p for p in v if (p in in_action_param_only)} for (k, v) in params.items()}
    iapo = {k: v for (k, v) in iapo.items() if v}

    i = 'in_action_param_only/all: {lap}/{ap}\n\nВ action.c:\n{acdt}\n\nВсе:\n{adt}'.format(
        lap=len(in_action_param_only),
        ap=len(all_p),
        adt='\n'.join(str([stri, len(params[stri]), params[stri]]) for stri in sorted(params)),
        acdt='\n'.join(str([stri, len(iapo[stri]), iapo[stri]]) for stri in sorted(iapo)),
    )
    lr_vars.Logger.info(i)

    if ask2:
        text = '\n'.join(in_action_param_only)
        cf = CREATE_or_FIND(wrsp_create)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[cf, K_SKIP],
            default_key=cf,
            title='3.2) ответ: Поиск param по regexp с постобработкой',
            is_text=text,
            text_before='3) Поиск param в тексте {ps}:\n\nпо regexp и дальнейшей обработке результата.\n'
                        'найдено {ln} шт'.format(ps=params_source, ln=len(in_action_param_only), ),
            text_after='добавить/удалить: необходимо удалить "лишнее", то что не является param',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )

        if y.ask() == cf:
            yt = y.text.split('\n')
            in_action_param_only = lr_lib.core_gui.group_param.gp_filter.param_sort(yt, deny_param_filter=False)
        else:
            return []

    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, in_action_param_only, widget=action.tk_text, ask=False)
    return in_action_param_only
