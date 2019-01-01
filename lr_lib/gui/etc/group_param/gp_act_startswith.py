# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, по началу имени param

import lr_lib
import lr_lib.gui.widj.dialog
from lr_lib.core.etc.lbrb_checker import check_bound_lb
from lr_lib.gui.etc.group_param.gp_filter import param_sort
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.gp_var import K_FIND, K_SKIP, K_CANCEL


def group_param_search(action: 'lr_lib.gui.action.main_action.ActionWindow') -> ["zkau_5650", "zkau_5680", ]:
    """поиск в action.c, всех уникальных param, в имени которых есть param_part"""
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_CANCEL],
        default_key=K_CANCEL,
        title='поиск param в action, используя начало param имен',
        is_text='\n'.join(lr_vars.Params_names),
        text_before='В action.c тексте, будет произведен поиск param, имя которых начинается на указанные имена.',
        text_after='добавить/удалить',
        parent=action,
    )

    ans = y.ask()
    params = set()

    if ans == K_FIND:
        param_parts = set(filter(str.strip, y.text.split('\n')))
        for part in param_parts:  # "zkau_"
            ps = _group_param_search(action, part)
            ps = param_sort(ps)
            params.update(ps)
            continue
    else:
        return params

    params = param_sort(params)

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_SKIP],
        default_key=K_FIND,
        title='Имена param',
        is_text='\n'.join(params),
        text_before='найдено {} шт'.format(len(params)),
        text_after='добавить/удалить',
        parent=action,
        color=lr_vars.PopUpWindColor1,
    )
    ans = y.ask()

    # создание param
    if ans == K_FIND:
        params = y.text.split('\n')
    else:
        return []

    params = param_sort(params)
    return params


def _group_param_search(action: 'lr_lib.gui.action.main_action.ActionWindow',
                        param_part: "zkau_",
                        part_mode=True, allow=lr_lib.core.wrsp.param.wrsp_allow_symb,
                        ) -> iter(("zkau_5650", "zkau_5680",)):
    """поиск в action.c, всех param, в имени которых есть param_part / или по LB"""
    for web_ in action.web_action.get_web_snapshot_all():
        split_text = web_.get_body().split(param_part)

        for index in range(len(split_text) - 1):
            left = split_text[index]
            left = left.rsplit('\n', 1)
            left = left[-1].lstrip()
            right = split_text[index + 1]
            right = right.split('\n', 1)
            right = right[0].rstrip()

            if part_mode:
                st = check_bound_lb(left)
            else:
                st = (right[0] in allow)

            if st:
                param = []  # "5680"

                for s in right:
                    if s in allow:
                        param.append(s)
                    else:
                        break
                    continue

                if param:
                    param = ''.join(param)
                    if part_mode:  # param_part или по LB
                        param = (param_part + param)

                    yield param  # "zkau_5680"
            continue
        continue
    return


def run_in_end_param_from_param(action: 'lr_lib.gui.action.main_action.ActionWindow', exist_params: [str, ]) -> [str, ]:
    """поиск по началу имени - взять n первых символов для повторного поиска param по началу имени"""
    param_spin = lr_vars.SecondaryParamLen.get()
    if not param_spin:
        return []

    params = set()
    for param in exist_params:  # params.update
        part = param[:param_spin]
        ap = _group_param_search(action, part)
        params.update(ap)
        continue

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_SKIP],
        default_key=K_FIND,
        title='Имена param, поиск в action.c',
        is_text='\n'.join(params),
        text_before='поиск в action.c, по началу имени - взять n первых символов '
                    'для повторного поиска param по началу имени\nнайдено {} шт'.format(len(params)),
        text_after='добавить/удалить',
        parent=action,
        color=lr_vars.PopUpWindColor1,
    )
    ans = y.ask()

    # создание param
    if ans == K_FIND:
        params = y.text.split('\n')
    else:
        return []

    params = param_sort(params)
    return params