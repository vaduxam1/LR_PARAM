# -*- coding: UTF-8 -*-
# нахождение param, в action.c файле, по началу имени param

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_job
import lr_lib.gui.widj.dialog
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP, K_CANCEL, CREATE_or_FIND


def group_param_search_by_name(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source,
        wrsp_create=False,
        text=None,
        ask=True,
        ask2=True,
        action_text=True,
) -> ["zkau_5650", "zkau_5680", ]:
    """поиск в action.c, всех уникальных param, в имени которых есть param_part"""
    if text is None:
        if ask:
            y = lr_lib.gui.widj.dialog.YesNoCancel(
                [K_FIND, K_CANCEL],
                default_key=K_FIND,
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
                return ()
            text = y.text
        else:
            text = lr_lib.core.var.vars_param.Params_names

    if isinstance(text, str):
        param_parts = text.split('\n')
    else:
        param_parts = text

    param_parts = filter(str.strip, param_parts)
    param_parts = set(param_parts)

    params = lr_lib.core_gui.group_param.gp_job._group_param_search_by_param_part(param_parts, params_source)
    if action_text and (not isinstance(action_text, str)):
        action_text = action.web_action._all_web_body_text()
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, action_text=action_text)

    if ask2:
        cf = CREATE_or_FIND(wrsp_create)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [cf, K_SKIP],
            default_key=cf,
            title='1.2) ответ',
            is_text='\n'.join(params),
            text_before='1) найдено {} шт'.format(len(params)),
            text_after='добавить/удалить',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()

        # создание param
        if ans == cf:
            params = y.text.split('\n')
        else:
            return []

        params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
    if wrsp_create:  # создать wrsp
        lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=action.tk_text, ask=False)
    return params


def group_param_search_by_exist_param(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source,
        exist_params=(),
        wrsp_create=False,
        action_text=True,
        ask=True,
        ask2=True,
        add=True,
) -> [str, ]:
    """поиск по началу имени - взять n первых символов для повторного поиска param по началу имени"""
    if add:
        exist_params = list(exist_params)
        exist_params.extend(lr_lib.core.var.vars_param.Params_names)

    if ask:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_SKIP],
            default_key=K_FIND,
            title='поиск {param} по началу имени',
            is_text='\n'.join(exist_params),
            text_before='итого {} шт.'.format(len(exist_params)),
            text_after='добавить/удалить',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()
        # создание param
        if ans == K_FIND:
            exist_params = list(filter(bool, y.text.split('\n')))
        else:
            return []

    params = lr_lib.core_gui.group_param.gp_job._group_param_search_by_exist_param(exist_params, params_source)
    if action_text and (not isinstance(action_text, str)):
        action_text = action.web_action._all_web_body_text()
    params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, action_text=action_text)

    if ask2:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_SKIP],
            default_key=K_FIND,
            title='5) запрос/ответ: Имена param, поиск в action.c',
            is_text='\n'.join(params),
            text_before='5) Поиск param в [ ACTION.C ] тексте:\n\n'
                        'Для всех param, найденных предыдущими способами - взять {n} первых символов имени,\n'
                        'и использовать для повторного поиска param по началу имени\n\n'
                        'найдено {ln} шт'.format(ln=len(params), n=lr_vars.SecondaryParamLen.get(), ),
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
