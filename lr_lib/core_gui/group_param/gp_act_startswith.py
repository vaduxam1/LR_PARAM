# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, по началу имени param

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.gui.widj.dialog
from lr_lib.core.var import vars as lr_vars
from lr_lib.core_gui.group_param.gp_var import K_FIND, K_SKIP, K_CANCEL


def group_param_search_by_name(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        wrsp_create=False,
        text=None,
) -> ["zkau_5650", "zkau_5680", ]:
    """поиск в action.c, всех уникальных param, в имени которых есть param_part"""
    if text is None:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_CANCEL],
            default_key=K_CANCEL,
            title='1.1) запрос: поиск param в action, используя начало param имен',
            is_text='\n'.join(lr_lib.core.var.vars_param.Params_names),
            text_before='1) Поиск param в [ ACTION.C ] тексте: '
                        'Поиск param, имя которых начинается на указанные имена.\n'
                        'Например используя ( "zkau_" ), для action.c файла подобного содержания:\n\n'
                        'web_url("index.zul",\n'
                        '... "value=zkau_1"; ... value=editZul_1;...\n... value={editZul_2, "zkau_2"} ...\n'
                        '... "item=zkau_3"; ... item=editZul_3; ...\n... item={editZul_4, "zkau_4"} ...\nLAST);\n\n'
                        'можно найти такие param: zkau_1, zkau_2, zkau_3, zkau_4.',
            text_after='добавить/удалить',
            parent=action,
        )

        ans = y.ask()
        if ans != K_FIND:
            return []
        text = y.text

    params = set()
    stext = text.split('\n')
    param_parts = set(filter(str.strip, stext))

    for part in param_parts:  # "zkau_"
        ps = _group_param_search(action, part)
        ps = lr_lib.core_gui.group_param.gp_filter.param_sort(ps)
        params.update(ps)
        continue

    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params)

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        [K_FIND, K_SKIP],
        default_key=K_FIND,
        title='1.2) ответ',
        is_text='\n'.join(params),
        text_before='1) найдено {} шт'.format(len(params)),
        text_after='добавить/удалить',
        parent=action,
        color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
    )
    ans = y.ask()

    # создание param
    if ans == K_FIND:
        params = y.text.split('\n')
    else:
        return []

    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params)
    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return params


def _group_param_search(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        param_part: "zkau_",
        part_mode=True,
        allow=lr_lib.core.wrsp.param.wrsp_allow_symb,
        texts_for_search=None,
) -> iter(("zkau_5650", "zkau_5680",)):
    """
    поиск в action.c, всех param, в имени которых есть param_part / или по LB
    part_mode=False - поиск param в action, по LB=
    texts_for_search - None: в action.c / [str, ]: для поиска в файлах ответов
    """
    if texts_for_search is None:
        texts_for_search = ((web_.snapshot, web_.get_body()) for web_ in action.web_action.get_web_snapshot_all())

    for (_file, text) in texts_for_search:
        split_text = text.split(param_part)

        for index in range(len(split_text) - 1):
            left = split_text[index]
            left = left.rsplit('\n', 1)
            left = left[-1].lstrip()
            right = split_text[index + 1]
            right = right.split('\n', 1)
            right = right[0].rstrip()

            if part_mode:
                st = lr_lib.core.etc.lbrb_checker.check_bound_lb(left)
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


def group_param_search_by_exist_param(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        exist_params: [str, ],
        wrsp_create=False,
) -> [str, ]:
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
        title='5) запрос/ответ: Имена param, поиск в action.c',
        is_text='\n'.join(params),
        text_before='5) Поиск param в [ ACTION.C ] тексте:\n\n'
                    'Для всех param, найденных предыдущими способами - взять {n} первых символов имени,\n'
                    'и использовать для повторного поиска param по началу имени\n\n'
                    'найдено {ln} шт'.format(ln=len(params), n=param_spin, ),
        text_after='добавить/удалить',
        parent=action,
        color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
    )
    ans = y.ask()

    # создание param
    if ans == K_FIND:
        params = y.text.split('\n')
    else:
        return []

    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return params
