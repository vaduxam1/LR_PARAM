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


TB1 = '''
5) Поиск param в [ ACTION.C ] тексте: Поиск param, имя которых начинается на указанные имена.

Например используя ( "zkau_" ), для action.c файла подобного содержания:
    web_url("index.zul",
    ... "value=zkau_1"; ... value=editZul_1;...\n... value={editZul_2, "zkau_2"} ...
    ... "item=zkau_3"; ... item=editZul_3; ...\n... item={editZul_4, "zkau_4"} ...\nLAST);
можно найти такие param: zkau_1, zkau_2, zkau_3, zkau_4.'

найдено %s шт
'''.strip()


def group_param_search_by_name(
        action: 'lr_lib.gui.action.main_action.ActionWindow',
        params_source,
        wrsp_create=False,
        text=None,
        ask=True,
        ask2=True,
        action_text=True,
) -> ["zkau_5650", "zkau_5680", ]:
    """
    поиск в action.c, всех уникальных param, в имени которых есть param_part
    """
    if text is None:
        if ask:
            y = lr_lib.gui.widj.dialog.YesNoCancel(
                [K_FIND, K_CANCEL],
                default_key=K_FIND,
                title='5.1) запрос: поиск param в action, используя начало param имен',
                is_text='\n'.join(lr_lib.core.var.vars_param.Params_names),
                text_before=(TB1 % len(lr_lib.core.var.vars_param.Params_names)),
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
            title='5.2) ответ',
            is_text='\n'.join(params),
            text_before=(TB1 % len(params)),
            text_after='добавить/удалить: необходимо удалить "лишнее", то что не является param',
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


TB2 = '''
5) Поиск param в [ ACTION.C ] тексте:
Для всех param, найденных предыдущими способами - взять {n} первых символов имени,
и использовать для повторного поиска param по началу имени.

найдено {ln} шт
'''.strip()


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
    """
    поиск по началу имени - взять n первых символов для повторного поиска param по началу имени
    """
    if add:
        exist_params = list(exist_params)
        exist_params.extend(lr_lib.core.var.vars_param.Params_names)
        exist_p = list(action.web_action.websReport.wrsp_and_param_names.values())
        exist_params.extend(exist_p)  # использовать уже созданные param

    if ask:
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_SKIP],
            default_key=K_FIND,
            title='5.1) запрос: LAST поиск {param} по началу имени',
            is_text='\n'.join(exist_params),
            text_before=TB2.format(ln=len(exist_params), n=lr_vars.SecondaryParamLen.get()),
            text_after='добавить/удалить',
            parent=action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()
        # создание param
        if ans == K_FIND:
            ts = y.text.split('\n')
            exist_params = list(filter(bool, ts))
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
            title='5.2) ответ: LAST поиск {param} по началу имени',
            is_text='\n'.join(params),
            text_before=TB2.format(ln=len(params), n=lr_vars.SecondaryParamLen.get(), ),
            text_after='добавить/удалить: необходимо удалить "лишнее", то что не является param',
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
