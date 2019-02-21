# -*- coding: UTF-8 -*-
# нахождение param, в файлах ответов split

from typing import Iterable

import lr_lib
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_start
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_job
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP, CREATE_or_FIND

TT1 = '''
4) Поиск param str.split('&') способом.

найдено {} шт'
'''.strip()

def group_param_search_by_split(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source,
        wrsp_create=False,
        action_text=True,
        ask=True,
        ask2=True,
        **kwargs,
) -> [str, ]:
    """
    поиск param в RequestBody/RequestHeader файлах
    """
    params = set()
    param_texts = lr_lib.core_gui.group_param.gp_job._text_from_params_source(params_source)
    for param in split(param_texts):
        params.add(param)  # добавить
        continue

    ats = isinstance(action_text, str)
    if action_text and (not ats):
        action_text = action.web_action._all_web_body_text()
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, action_text=action_text)

    if ask2:
        cf = CREATE_or_FIND(wrsp_create)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [cf, K_SKIP],
            default_key=cf,
            title='4) запрос/ответ: split Поиск param в RequestBody/RequestHeader файлах.',
            is_text='\n'.join(params),
            text_before=TT1.format(len(params)),
            text_after='добавить/удалить: необходимо удалить "лишнее", то что не является param',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()

        # создание param
        if ans == cf:
            params = y.text.split('\n')
            params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
        else:
            return []

    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)

    return params


denySymb = ' %'  # запрещенный символы в param
allowParamFilter = lambda param: (not any(d in param for d in denySymb))
NullSymb = '''"'''  # заменить на ''


def split(param_texts: ([str, str],), ) -> Iterable[str]:
    """
    найти param, split способом
    """
    for (file, text_) in param_texts:
        for text in text_.split('\n'):
            st = text.split('=')

            for sa in st[1:]:
                pa = sa.split('&')[0]

                if '%' in pa:
                    params = pa.split('%22')
                else:
                    params = [pa]

                for param in filter(allowParamFilter, params):
                    for s in NullSymb:
                        param = param.replace(s, '')
                        continue
                    param = param.strip()

                    yield param
                    continue
                continue
            continue
        continue
    return