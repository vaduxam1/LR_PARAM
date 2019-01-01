# -*- coding: UTF-8 -*-
# ядро - нахождение и замена group_param

import sys
import queue

import lr_lib
from lr_lib.core.etc.lbrb_checker import check_bound_lb
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.gp_act_lb import session_params
from lr_lib.gui.etc.group_param.gp_filter import param_sort
from lr_lib.gui.etc.group_param.gp_act_startswith import _group_param_search
from lr_lib.gui.etc.group_param.gp_progress import ProgressBar
from lr_lib.gui.etc.group_param.gp_var import K_FIND, K_SKIP, K_CANCEL


@lr_vars.T_POOL_decorator
def group_param(event, widget=None, params=None, ask=True) -> None:
    """gui - нахождение и замена для группы web_reg_save_param's"""
    if widget is None:
        widget = event.widget
    if not params:
        params = _find_params(widget, params=params)
        params = param_sort(params)
        if not params:
            lr_vars.Logger.warning('param не найдены! {}'.format(params), parent=widget.action)
            return
    # пользовательское редактирование params
    ap = _ask_params(params, widget.action, ask=ask)
    (len_params, params) = ap
    if not len_params:
        return
    # заменить params
    with lr_vars.Window.block(force=True):
        with widget.action.block():
            widget.action.backup()
            with ProgressBar(len_params, widget) as progress_bar:
                # создание
                create_iterator = _group_param_iter(params, widget.action)
                # прогресс
                for item in create_iterator:
                    progress_bar.update(item)
                    continue
    return


def _find_params(widget, params: '([str, ] or False or None)') -> [str, ]:
    """при params == False or None - найти params в widget"""
    if params is None:  # поиск только по началу имени
        selection = widget.selection_get()
        params = list(_group_param_search(widget.action, selection))
    elif params is False:  # поиск только по LB=
        selection = widget.selection_get()
        params = session_params(widget.action, lb_list=[selection], ask=False)
    return params


def _ask_params(params: [str, ], action: 'lr_lib.gui.action.main_action.ActionWindow', ask=True) -> (int, [str, ]):
    """спросить о создании params, -> 0 - не создавать"""
    old_len_params = len(params)
    if ask:
        pc = '{0} шт.'.format(old_len_params)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[K_FIND, K_CANCEL, K_SKIP],
            default_key=K_FIND,
            title=pc,
            is_text='\n'.join(params),
            text_before='найти group param',
            text_after=pc,
            parent=action,
        )
        ask = y.ask()

        if ask == K_FIND:
            yt = y.text.split('\n')
            params = param_sort(yt, deny_param_filter=False)
        elif ask == K_SKIP:
            params = []
        else:
            item = (0, [])
            return item

    new_len_params = len(params)
    lr_vars.Logger.info('Имеется {l} ранее созданных param.\nДля создания выбрано/найдено {p}/{_p} param.\n'.format(
        _p=old_len_params, p=new_len_params, l=len(action.web_action.websReport.wrsp_and_param_names)))

    item = (new_len_params, params)
    return item


def _group_param_iter(params: [str, ],
                      action: 'lr_lib.gui.action.main_action.ActionWindow',
                      ) -> iter((int, dict, str, [str, ]),):
    """
    ядро - найти и заменить группу web_reg_save_param
    """
    wrsp_dict_queue = queue.Queue()
    unsuccess = []  # params, обработанные с ошибкой

    # запуск потока для создания wrsp_dict's param's в фоне
    _thread_wrsp_dict_creator(wrsp_dict_queue, params, unsuccess, action)

    web_actions = tuple(action.web_action.get_web_snapshot_all())
    replace = action.web_action.replace_bodys_iter(web_actions)  # сопрограмма-заменить
    next(replace)
    try:

        for (counter, wrsp_dict) in enumerate(iter(wrsp_dict_queue.get, None), start=1):
            wrsp = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)  # wrsp

            # вставить web_reg_save_param перед web
            action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)
            it = (wrsp_dict['param'], wrsp_dict['web_reg_name'])
            # заменить param на web_reg_save_param
            replace.send(it)

            try:  # продолжать при raise
                action.param_inf_checker(wrsp_dict, wrsp)  # проверка(popup окно) inf запроса <= inf web_reg_save_param
            except (UserWarning, AssertionError) as ex:
                pass

            item = (counter, wrsp_dict, wrsp, unsuccess)
            yield item  # для progressbar
            continue

    finally:
        action.web_action_to_tk_text(websReport=True)  # вставить в action.c
    return


@lr_vars.T_POOL_decorator
def _thread_wrsp_dict_creator(wrsp_dicts: queue.Queue, params: [str, ], unsuccess: [],
                              action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """ядро - создать wrsp_dicts в фоне, чтобы не терять время, при показе popup окон"""
    for param in params:
        try:
            lr_vars.VarParam.set(param, action=action, set_file=True)  # найти param, создать wrsp_dict
            dt = lr_vars.VarWrspDict.get()
            wrsp_dicts.put(dt)  # вернуть wrsp_dict
        except Exception:
            unsuccess.append(param)
            lr_lib.etc.excepthook.excepthook(*sys.exc_info())
        continue

    wrsp_dicts.put_nowait(None)  # exit
    return
