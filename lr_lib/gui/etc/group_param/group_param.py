# -*- coding: UTF-8 -*-
# нахождение и замена group_param
import re
import sys
import queue
import tkinter as tk

import lr_lib
from lr_lib.core.etc.lbrb_checker import check_bound_lb
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.group_param.group_progress import ProgressBar


K_FIND = 'Найти'
K_SKIP = 'Пропуск'
K_CANCEL = 'Отменить'


@lr_vars.T_POOL_decorator
def group_param(event, widget=None, params=None, ask=True) -> None:
    """gui - нахождение и замена для группы web_reg_save_param's"""
    if widget is None:
        widget = event.widget
    if not params:
        params = _find_params(widget, params=params)
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
        params = group_param_search(widget.action, selection)
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
            return (0, [])

    new_len_params = len(params)
    lr_vars.Logger.info('Имеется {l} ранее созданных param.\nДля создания выбрано/найдено {p}/{_p} param.\n'.format(
        _p=old_len_params, p=new_len_params, l=len(action.web_action.websReport.wrsp_and_param_names)))

    it = (new_len_params, params)
    return it


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


def group_param_search(action: 'lr_lib.gui.action.main_action.ActionWindow',
                       param_part: "zkau_") -> ["zkau_5650", "zkau_5680", ]:
    """поиск в action.c, всех уникальных param, в имени которых есть param_part"""
    params = _group_param_search(action, param_part)
    params = param_sort(params)
    return params


def _group_param_search(action: 'lr_lib.gui.action.main_action.ActionWindow', param_part: "zkau_",
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


def session_params(action: 'lr_lib.gui.action.main_action.ActionWindow', lb_list=None, ask=True, ) -> list:
    """поиск param в action, по LB="""
    if lb_list is None:
        lb_list = lr_vars.LB_PARAM_FIND_LIST

    if ask:
        text = action.tk_text.get(1.0, tk.END)

        # что за param?
        lb_uuid = re.findall(r'uuid_\d=', text)
        lb_col_count = re.findall(r'p_p_col_count=\d&', text)

        ts = set(lb_list + lb_uuid + lb_col_count)
        text = '\n'.join(ts)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[K_FIND, K_SKIP],
            default_key=K_FIND,
            title='автозамена по LB=',
            is_text=text,
            text_before='найти param по LB=',
            text_after='указать LB, с новой строки',
            parent=action,
        )
        if y.ask() == K_FIND:
            lb_list = y.text.split('\n')
        else:
            return []

    params = []
    for lb_in_action in filter(str.strip, lb_list):
        ps = _group_param_search(action, lb_in_action, part_mode=False)
        params.extend(ps)
        continue

    params = param_sort(params)
    return params


def param_sort(params: [str, ], reverse=True, _filter=True, deny_param_filter=True, ) -> [str, ]:
    """
    отсортировать param по длине, тк если имеются похожие имена, лучше сначала заменять самые длинные,
    тк иначе например заменяя "zkau_1" - можно ошибочно заменить и для "zkau_11"
    """
    if _filter:
        params = param_filter(params, deny_param_filter=deny_param_filter, )
    params = sorted(params, key=len, reverse=reverse)
    return params


def param_filter(params: [str, ], len_p_min=lr_vars.MinParamLen, deny=lr_vars.DENY_PARAMS,
                 deny_param_filter=True, ) -> iter((str,)):
    """отфильтровать лишние param"""
    params = set(filter(str.strip, params))
    if deny_param_filter:
        for param in params:
            if param in deny:
                continue
            else:
                len_p = len(param)
                if len_p > len_p_min:
                    if param[len_p_min].isupper() and param.startswith('on'):
                        continue  # "onScreen"

                    yield param
            continue
    else:
        yield from params
    return
