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
            with lr_lib.core_gui.group_param.gp_progress.ProgressBar(len_params, widget).run() as progress_bar:
                for _ in map(progress_bar.update, _group_param_iter(params, action)):  # создание
                    continue  # прогрессбар
    return


def _group_param_iter(
        params: List[str],
        action: 'lr_lib.gui.action.main_action.ActionWindow',
) -> Iterable[Tuple[int, dict, str, List[str]]]:
    """
    ядро - найти и заменить группу web_reg_save_param - старый/новый способ
    """
    if lr_vars.WRSPCreateMultiParamMode.get():
        yield from _group_param_iter2(params, action)
    else:
        yield from _group_param_iter1(params, action)
    return


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
            # заменить param на web_reg_save_param
            replace.send((wrsp_dict['param'], wrsp_dict['web_reg_name']))

            try:  # проверка(popup окно) inf запроса <= inf web_reg_save_param
                action.param_inf_checker(wrsp_dict, wrsp)
            except (UserWarning, AssertionError) as ex:
                pass  # продолжать при raise
            except Exception:
                continue

            yield counter, wrsp_dict, wrsp, unsuccess  # для progressbar
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
    web_actions = tuple(action.web_action.get_web_snapshot_all())
    wrsp_p_inf = all_param_inf(params, web_actions)
    if not wrsp_p_inf:
        return
    unsuccess = []  # params, обработанные с ошибкой
    all_wrsp = all_wrsp_variant(params, unsuccess, action)  # все варианты wrsp
    flf = lr_vars.VarFirstLastFile.get()

    for (counter, param) in enumerate(wrsp_p_inf, start=1):
        try:
            i_wrsp_infs = all_wrsp[param]  # все inf/wrsp для param
            param_usage_infs = wrsp_p_inf[param]  # все inf использования данного param
            assert i_wrsp_infs and param_usage_infs
        except:
            unsuccess.append(param)
            continue

        if len(i_wrsp_infs) > 1:
            wrsp_and_param_infs = many_param_from_one(i_wrsp_infs, param_usage_infs, unsuccess, param, flf)
            # other_same_param = [(*i_wrsp_infs[i_wrsp], min(v), max(v)) for (i_wrsp, v) in wrsp_and_param_infs.items()]
            other_same_param = []
            for (i_wrsp, v) in wrsp_and_param_infs.items():
                (wrsp_dict, wrsp_text) = i_wrsp_infs[i_wrsp]
                wrsp_dict = wrsp_dict.copy()
                mav = max(v)
                wrsp_dict['max_action_inf'] = wrsp_dict['param_max_action_inf'] = miv = min(v)
                s = (wrsp_dict, wrsp_text, miv, mav)
                other_same_param.append(s)
                continue
            yield counter, other_same_param[0][0], other_same_param[0][1], unsuccess  # для progressbar
        else:
            last = sorted(i_wrsp_infs)[-1]
            (wrsp_dict, wrsp_text) = i_wrsp_infs[last]
            other_same_param = [(wrsp_dict, wrsp_text, min(param_usage_infs), max(param_usage_infs)), ]
            yield counter, wrsp_dict, wrsp_text, unsuccess  # для progressbar

        # замена param
        for (wrsp_dict, wrsp_text, i_min, i_max) in other_same_param:
            try:
                replace_body(action, web_actions, wrsp_dict, wrsp_text, i_min, i_max)
            except:
                unsuccess.append(param)
                lr_lib.etc.excepthook.excepthook()
            # yield counter, wrsp_dict, wrsp_text, unsuccess  # для progressbar
            continue
        continue

    # показать новый action.c
    action.web_action_to_tk_text(websReport=True)
    return


def many_param_from_one(i_wrsp_infs, param_usage_infs, unsuccess, param, flf) -> Dict:
    """несколько wrsp из одного param"""
    wrsp_and_param_infs = {}
    last_i_wrsp = 0
    last_wr = {}
    wrsp_create_infs = sorted(i_wrsp_infs)

    for i_param in param_usage_infs:
        _i = []

        for i_wrsp in wrsp_create_infs:
            if i_wrsp < i_param:
                if last_wr:
                    curr_wr = i_wrsp_infs[i_wrsp][0]
                    (lb1, rb1) = (last_wr['lb'], last_wr['rb'])
                    (lb2, rb2) = (curr_wr['lb'], curr_wr['rb'])
                    if (lb1 == lb2) and (rb1 == rb2):
                        continue
                _i.append(i_wrsp)
                last_wr = i_wrsp_infs[i_wrsp][0]
            else:
                break
            continue

        if _i:  # создать новый wrsp
            last_i_wrsp = _i[-1 if flf else 0]
            try:
                wrsp_and_param_infs[last_i_wrsp].append(i_param)
            except:
                wrsp_and_param_infs[last_i_wrsp] = [i_param]
        elif last_i_wrsp:  # использовате предыдущий wrsp
            wrsp_and_param_infs[last_i_wrsp].append(i_param)

        else:  # param используется в том же inf что и определяется
            for i_wrsp in wrsp_create_infs:
                if i_wrsp == i_param:
                    if last_wr:
                        curr_wr = i_wrsp_infs[i_wrsp][0]
                        (lb1, rb1) = (last_wr['lb'], last_wr['rb'])
                        (lb2, rb2) = (curr_wr['lb'], curr_wr['rb'])
                        if (lb1 == lb2) and (rb1 == rb2):
                            continue
                    _i.append(i_wrsp)
                    last_wr = i_wrsp_infs[i_wrsp][0]
                    break
                continue
            if _i:
                last_i_wrsp = _i[0]
                try:
                    wrsp_and_param_infs[last_i_wrsp].append(i_param)
                except:
                    wrsp_and_param_infs[last_i_wrsp] = [i_param]
            else:
                unsuccess.append(param)
        continue
    return wrsp_and_param_infs


def all_param_inf(params: List[str], web_actions) -> Dict:
    """все inf где есть param"""
    wrsp_p_inf = {}
    for w in web_actions:
        for param in params:
            i_wrsp = w.is_param_in_body(param)
            if i_wrsp:
                try:
                    wrsp_p_inf[param].append(i_wrsp)
                except:
                    wrsp_p_inf[param] = [i_wrsp]
            continue
        continue
    return wrsp_p_inf


def all_wrsp_variant(params: List[str], unsuccess: List, action) -> Dict:
    """все варианты wrsp"""
    all_wrsp = {}
    for param in params:
        try:
            wds = lr_lib.core_gui.all_wrsp.all_wrsp_dict_web_reg_save_param_no_tr(param, action=action, create=False)
            all_wrsp[param] = ap = {}
            for wd in wds:
                i_wrsp = wd[0]['inf_nums'][0]
                if i_wrsp in all_wrsp:  # wrsp из одного inf
                    (lb1, rb1) = (wd[0]['lb'], wd[0]['rb'])
                    (lb2, rb2) = (ap[i_wrsp][0]['lb'], ap[i_wrsp][0]['rb'])
                    rl1 = len(rb1)
                    rl2 = len(rb2)
                    if (rl2 > rl1) or ((rl2 == rl1) and (len(lb2) > len(lb1))):
                        continue  # оставить более длинные
                else:
                    ap[i_wrsp] = wd
                continue
        except Exception as ex:
            unsuccess.append(param)
            lr_lib.etc.excepthook.excepthook(ex)
        continue
    return all_wrsp


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
        lr_lib.etc.excepthook.excepthook()

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
