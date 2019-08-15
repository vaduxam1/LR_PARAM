# -*- coding: UTF-8 -*-
# ядро - нахождение и замена group_param

import queue
from typing import Iterable, Tuple, List, Dict

import lr_lib
import lr_lib.core.var.etc.vars_other
import lr_lib.core_gui.action_lib
import lr_lib.core_gui.group_param.gp_progress
import lr_lib.core_gui.group_param.gp_var
import lr_lib.etc.excepthook
import lr_lib._next_34
import lr_lib.core_gui.all_wrsp
from lr_lib.core.var import vars as lr_vars


@lr_lib.core.var.etc.vars_other.T_POOL_decorator
def group_param(event, params: List[str], widget=None, ask=True) -> None:
    """
    нахождение и замена для группы web_reg_save_param's
    """
    if widget is None:
        widget = event.widget
    action = lr_lib.core_gui.action_lib.event_action_getter(event)

    # пользовательское редактирование params
    ap = lr_lib.core_gui.group_param.gp_var._ask_params(params, action, ask=ask)
    (len_params, params) = ap
    if not len_params:
        return

    # заменить params
    with lr_vars.Window.block(force=True):
        with action.block():
            action.backup()
            progress_bar = lr_lib.core_gui.group_param.gp_progress.ProgressBar(len_params, widget)
            progress_bar.__enter__()
            try:  # создание
                create_iterator = _group_param_iter(params, action)
                # прогресс
                for item in create_iterator:
                    progress_bar.update(item)
                    continue
            except:
                lr_lib.etc.excepthook.excepthook()
            finally:
                progress_bar.__exit__(None, None, None)
    return


def _group_param_iter(
        params: List[str],
        action: 'lr_lib.gui.action.main_action.ActionWindow',
) -> Iterable[Tuple[int, dict, str, List[str]]]:
    """
    ядро - найти и заменить группу web_reg_save_param - старый/новый способ
    """
    if lr_vars.WRSPCreateMultyParamMode.get():
        return _group_param_iter2(params, action)
    return _group_param_iter1(params, action)


def _group_param_iter1(
        params: List[str],
        action: 'lr_lib.gui.action.main_action.ActionWindow',
) -> Iterable[Tuple[int, dict, str, List[str]]]:
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
    wrsp_get = iter(wrsp_dict_queue.get, None)
    try:

        for (counter, wrsp_dict) in enumerate(wrsp_get, start=1):
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
            except Exception:
                continue

            item = (counter, wrsp_dict, wrsp, unsuccess)
            yield item  # для progressbar
            continue

    finally:  # показать новый action.c
        action.web_action_to_tk_text(websReport=True)
    return


def _group_param_iter2(
        params: List[str],
        action: 'lr_lib.gui.action.main_action.ActionWindow',
) -> Iterable[Tuple[int, dict, str, List[str]]]:
    """
    ядро - найти и заменить группу web_reg_save_param
    """
    unsuccess = []  # params, обработанные с ошибкой

    all_wrsp = {}
    for param in params:
        try:
            wds = lr_lib.core_gui.all_wrsp.all_wrsp_dict_web_reg_save_param_no_tr(param, action=action, create=False)
            all_wrsp[param] = {wd[0]['inf_nums'][0]: wd for wd in wds}
        except Exception as ex:
            unsuccess.append(param)
            lr_lib.etc.excepthook.excepthook(ex)
        continue

    web_actions = tuple(action.web_action.get_web_snapshot_all())
    wa_inf = {}
    for w in web_actions:
        for param in params:
            i = w.is_param_in_body(param)
            if i:
                try:
                    wa_inf[param].append(i)
                except:
                    wa_inf[param] = [i]
            continue
        continue
    if not wa_inf:
        return

    flf = lr_vars.VarFirstLastFile.get()

    for (counter, param) in enumerate(wa_inf, start=1):
        try:
            i_wrsp_infs = all_wrsp[param]
        except:
            unsuccess.append(param)
            continue
        try:
            i_infs = wa_inf[param]
        except:
            unsuccess.append(param)
            continue
        if (not i_wrsp_infs) or (not i_infs):
            continue

        if len(i_wrsp_infs) > 1:
            wr_pm = {}
            last_wr = {}

            for i_param in i_infs:
                wrsp_i = sorted(i_wrsp_infs)

                _i = []
                for i in wrsp_i:
                    curr_wr = i_wrsp_infs[i][0]
                    if i < i_param:
                        if last_wr:
                            (lb1, rb1) = (last_wr['lb'], last_wr['rb'])
                            (lb2, rb2) = (curr_wr['lb'], curr_wr['rb'])
                            if (lb1 == lb2) and (rb1 == rb2):
                                continue
                        _i.append(i)
                        last_wr = i_wrsp_infs[i][0]
                    continue

                if not _i:  # param используется в том же inf что и определяется
                    for i in wrsp_i:
                        curr_wr = i_wrsp_infs[i][0]
                        if i == i_param:
                            if last_wr:
                                (lb1, rb1) = (last_wr['lb'], last_wr['rb'])
                                (lb2, rb2) = (curr_wr['lb'], curr_wr['rb'])
                                if (lb1 == lb2) and (rb1 == rb2):
                                    continue
                            _i.append(i)
                            last_wr = i_wrsp_infs[i][0]
                        continue

                if _i:
                    last_i_wrsp = _i[-1 if flf else 0]

                    try:
                        wr_pm[last_i_wrsp].append(i_param)
                    except:
                        wr_pm[last_i_wrsp] = [i_param]
                continue

            other_same_param = [(*i_wrsp_infs[i], min(v), max(v)) for (i, v) in wr_pm.items()]

        else:
            last = sorted(i_wrsp_infs)[-1]
            (wrsp_dict, wrsp_text) = i_wrsp_infs[last]
            other_same_param = [(wrsp_dict, wrsp_text, min(i_infs), max(i_infs)), ]

        for (wrsp_dict, wrsp_text, i_min, i_max) in other_same_param:
            try:
                replace_body(action, web_actions, wrsp_dict, wrsp_text, i_min, i_max)
            except:
                unsuccess.append(param)
                raise

            yield counter, wrsp_dict, wrsp_text, unsuccess  # для progressbar
            continue
        continue

    # показать новый action.c
    action.web_action_to_tk_text(websReport=True)
    return


def replace_body(action, web_actions, wrsp_dict, wrsp_text, i_min, i_max) -> None:
    """замена param в web body"""
    replace = action.web_action.replace_bodys_iter(web_actions, min_inf=i_min, max_inf=i_max)  # заменить
    next(replace)

    # вставить web_reg_save_param перед web
    action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp_text)

    # заменить param на web_reg_save_param
    replace.send([wrsp_dict['param'], wrsp_dict['web_reg_name']])

    try:  # проверка(popup окно) inf запроса <= inf web_reg_save_param
        action.param_inf_checker(wrsp_dict, wrsp_text)
    except (UserWarning, AssertionError) as ex:
        pass  # продолжать при raise
    except Exception:
        raise

    return


@lr_lib.core.var.etc.vars_other.T_POOL_decorator
def _thread_wrsp_dict_creator(
        wrsp_dicts: 'queue.Queue',
        params: List[str],
        unsuccess: List[str],
        action: 'lr_lib.gui.action.main_action.ActionWindow',
) -> None:
    """
    ядро - создать wrsp_dicts в фоне, чтобы не терять время, при показе popup окон
    """
    for param in params:
        try:
            lr_vars.VarParam.set(param, action=action, set_file=True)  # найти param, создать wrsp_dict
            dt = lr_vars.VarWrspDict.get()
            wrsp_dicts.put(dt)  # вернуть wrsp_dict
        except Exception as ex:
            unsuccess.append(param)
            lr_lib.etc.excepthook.excepthook(ex)
        continue

    wrsp_dicts.put(None)  # exit
    return
