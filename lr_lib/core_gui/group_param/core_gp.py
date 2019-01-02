# -*- coding: UTF-8 -*-
# ядро - нахождение и замена group_param

import queue
import sys

import lr_lib
import lr_lib.core.var.vars_other
import lr_lib.core_gui.group_param.gp_progress
import lr_lib.core_gui.group_param.gp_var
from lr_lib.core.var import vars as lr_vars


@lr_lib.core.var.vars_other.T_POOL_decorator
def group_param(event, params: [str, ], widget=None, ask=True) -> None:
    """нахождение и замена для группы web_reg_save_param's"""
    if widget is None:
        widget = event.widget

    # пользовательское редактирование params
    ap = lr_lib.core_gui.group_param.gp_var._ask_params(params, widget.action, ask=ask)
    (len_params, params) = ap
    if not len_params:
        return

    # заменить params
    with lr_vars.Window.block(force=True):
        with widget.action.block():
            widget.action.backup()
            with lr_lib.core_gui.group_param.gp_progress.ProgressBar(len_params, widget) as progress_bar:
                # создание
                create_iterator = _group_param_iter(params, widget.action)
                # прогресс
                for item in create_iterator:
                    progress_bar.update(item)
                    continue
    return


def _group_param_iter(params: [str, ],
                      action: 'lr_lib.gui.action.main_action.ActionWindow',
                      ) -> iter((int, dict, str, [str, ]), ):
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
            wrsp = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)  # WRSP

            # вставить web_reg_save_param перед web
            action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)
            it = (wrsp_dict['param'], wrsp_dict['web_reg_name'])

            # заменить param на web_reg_save_param
            replace.send(it)

            try:  # проверка(popup окно) inf запроса <= inf web_reg_save_param
                action.param_inf_checker(wrsp_dict, wrsp)
            except (UserWarning, AssertionError) as ex:
                pass  # продолжать при raise

            item = (counter, wrsp_dict, wrsp, unsuccess)
            yield item  # для progressbar
            continue

    finally:  # показать новый action.c
        action.web_action_to_tk_text(websReport=True)
    return


@lr_lib.core.var.vars_other.T_POOL_decorator
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
