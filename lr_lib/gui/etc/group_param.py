# -*- coding: UTF-8 -*-
# команды из меню мыши - нахождение и замена group_param

import re
import sys
import queue
import threading
import contextlib

import tkinter as tk

import lr_lib.gui.etc.gui_other as lr_gui_other
import lr_lib.gui.widj.dialog as lr_dialog
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.core.etc.lbrb_checker as lr_lbrb_checker
import lr_lib.etc.excepthook as lr_excepthook


progress_str = '{proc}% : {counter}/{len_params} | fail={fail}\n{wrsp}'
final_str = '{state} | создано сейчас = {param} / fail={fail} : {unsuc} | всего {param_counter}'


@lr_vars.T_POOL_decorator
def group_param(event, widget=None, params=None, ask=True) -> None:
    """gui - нахождение и замена для группы web_reg_save_param's"""
    if widget is None:
        widget = event.widget

    # определить params
    if params is None:  # поиск только по началу имени
        params = group_param_search(widget.action, widget.selection_get())
    elif params is False:  # поиск только по LB=
        params = session_params(widget.action, lb_list=[widget.selection_get()], ask=False)
    if not params:
        return lr_vars.Logger.warning('param не найдены! %s' % params, parent=widget.action)

    _len_params = len(params)
    if ask:
        pc = '%s шт.' % _len_params
        y = lr_dialog.YesNoCancel(
            buttons=['Найти', 'Отменить', 'Пропуск'], text_before='найти group param', text_after=pc,
            is_text='\n'.join(params), title=pc, parent=widget.action, default_key='Найти')
        ask = y.ask()

        if ask == 'Найти':
            params = sorted(filter(bool, y.text.split('\n')), key=len, reverse=True)
        elif ask == 'Пропуск':
            params = []
        else:
            return

    len_params = len(params)
    lr_vars.Logger.info('Имеется {l} ранее созданных param.\nДля создания выбрано/найдено {p}/{_p} param.\n'.format(
        _p=_len_params, p=len_params, l=len(widget.action.web_action.websReport.wrsp_and_param_names)))

    # --- progressbar ---
    p1 = ((len_params / 100) or 1)
    
    def threadsafe_progress(lock=threading.Lock()):
        """threadsafe progressbar в потоке, тк одновременное warning popup-окно и прогрессбар блочат main поток"""
        with lock:
            __progressbar()

    def __progressbar() -> None:
        """progressbar выполнения, из local vars"""
        fail = len(unsuccess)

        if wrsp_dict:  # прогресс работы
            widget.action.toolbar['text'] = progress_str.format(
                counter=counter,
                len_params=len_params,
                fail=fail,
                proc=round(counter / p1),
                wrsp=wrsp,
            )
            widget.action.background_color_set(color=None)  # action цвет по кругу
            lr_vars.MainThreadUpdater.submit(lambda: lr_vars.T_POOL.submit(threadsafe_progress))  # перезапуск с задержкой

        else:  # выход - результаты работы
            param_counter = widget.action.param_counter(all_param_info=False)
            widget.action.toolbar['text'] = final_str.format(
                state=str(not fail).upper(),
                param_counter=param_counter,
                fail=fail,
                unsuc=(', '.join(unsuccess) if fail else ''),
                param=(len_params - fail),
            )
            if unsuccess:
                lr_vars.Logger.error('{} param не были обработаны:\n\t{}'.format(
                    fail, '\n\t'.join(unsuccess)), parent=widget.action)

            widget.action.background_color_set(color='')  # action оригинальный цвет
            widget.action.set_combo_len()
            lr_vars.Logger.debug(param_counter)

            if widget.action.final_wnd_var.get():
                lr_gui_other.repA(widget)
    # --- progressbar ---

    widget.action.backup()

    # заменить params
    with lr_vars.Window.block(force=True), widget.action.block(no_highlight=True):
        (counter, wrsp_dict, wrsp, unsuccess) = (0, {'param': ''}, '', [])  # начальные vars для progressbar

        lr_vars.T_POOL.submit(threadsafe_progress)
        for (counter, wrsp_dict, wrsp, unsuccess) in _group_param_iter(params, widget.action):  # заменить
            continue  # vars для progressbar

        wrsp_dict = None  # выход progressbar


def _group_param_iter(params: [str, ], action) -> iter((int, dict, str, [str, ]),):
    """ядро - найти и заменить группу web_reg_save_param"""
    unsuccess = []  # params, обработанные с ошибкой
    wrsp_dict_queue = queue.Queue()
    _thread_wrsp_dict_creator(wrsp_dict_queue, params, unsuccess, action)  # для param's, в фоне, создавать wrsp_dict's

    web_actions = tuple(action.web_action.get_web_snapshot_all())
    replace = action.web_action.replace_bodys_iter(web_actions)  # сопрограмма-заменить
    next(replace)
    try:
        for (counter, wrsp_dict) in enumerate(iter(wrsp_dict_queue.get, None), start=1):
            wrsp = lr_param.create_web_reg_save_param(wrsp_dict)

            # вставить web_reg_save_param перед web
            action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)
            # заменить param на web_reg_save_param
            replace.send((wrsp_dict['param'], wrsp_dict['web_reg_name']))

            with contextlib.suppress(UserWarning, AssertionError):  # продолжать при raise
                action.param_inf_checker(wrsp_dict, wrsp)  # проверка(popup окно) inf запроса <= inf web_reg_save_param
            yield (counter, wrsp_dict, wrsp, unsuccess)  # для progressbar
    finally:
        action.web_action_to_tk_text(websReport=True)  # вставить в action.c


@lr_vars.T_POOL_decorator
def _thread_wrsp_dict_creator(wrsp_dicts: queue.Queue, params: [str, ], unsuccess: [], action) -> None:
    """ядро - создать wrsp_dicts в фоне, чтобы не терять время, при показе popup окон"""
    for param in params:
        try:
            lr_vars.VarParam.set(param, action=action, set_file=True)  # найти param, создать wrsp_dict
            wrsp_dicts.put_nowait(lr_vars.VarWrspDict.get())  # вернуть wrsp_dict
        except Exception:
            unsuccess.append(param)
            lr_excepthook.excepthook(*sys.exc_info())

    wrsp_dicts.put_nowait(None)  # exit


@lr_vars.T_POOL_decorator
def auto_param_creator(action) -> None:
    """group params по кнопке PARAM - по LB + по началу имени"""
    y = lr_dialog.YesNoCancel(['Найти', 'Отменить'], is_text='\n'.join(lr_vars.Params_names), parent=action,
                              text_before='Будет произведен поиск param, имя которых начинается на указанные имена.',
                              title='начало param-имен', text_after='При необходимости - добавить/удалить')
    ans = y.ask()
    if ans == 'Найти':
        param_parts = list(filter(bool, map(str.strip, y.text.split('\n'))))

        params = set(session_params(action))  # поиск по LB=
        for part in param_parts:
            for param in group_param_search(action, part):
                params.add(param)  # поиск по началу имени

        params = [p for p in params if ((p not in lr_vars.DENY_PARAMS) and (
            not (len(p) > 2 and p.startswith('on') and p[2].isupper())))]
        params.sort(key=lambda param: len(param), reverse=True)

        y = lr_dialog.YesNoCancel(['Создать', 'Отменить'], is_text='\n'.join(params), parent=action,
                                  text_before='создание + автозамена. %s шт' % len(params), title='Имена param',
                                  text_after='При необходимости - добавить/удалить')
        ans = y.ask()
        if ans == 'Создать':
            params = list(filter(bool, map(str.strip, y.text.split('\n'))))
            group_param(None, widget=action.tk_text, params=params, ask=False)


def session_params(action, lb_list=None, ask=True) -> list:
    """поиск param в action, по LB="""
    if lb_list is None:
        lb_list = lr_vars.LB_PARAM_FIND_LIST

    if ask:
        text = action.tk_text.get(1.0, tk.END)
        lb_uuid = re.findall(r'uuid_\d=', text)
        lb_col_count = re.findall(r'p_p_col_count=\d&', text)

        text = '\n'.join(set(lb_list + lb_uuid + lb_col_count))
        y = lr_dialog.YesNoCancel(buttons=['Найти', 'Пропуск'], text_before='найти param по LB=',
                                  text_after='указать LB, с новой строки', is_text=text,
                                  title='автозамена по LB=',
                                  parent=action, default_key='Найти')
        if y.ask() == 'Найти':
            lb_list = y.text.split('\n')
        else:
            return []

    params = []
    for p in filter(bool, lb_list):
        params.extend(_group_param_search(action, p, part_mode=False))

    return list(reversed(sorted(p for p in set(params) if p not in lr_vars.DENY_PARAMS)))


def group_param_search(action, param_part: "zkau_") -> ["zkau_5650", "zkau_5680", ]:
    """поиск в action.c, всех уникальных param, в имени которых есть param_part"""
    params = list(set(_group_param_search(action, param_part)))  # уникальных
    params.sort(key=lambda param: len(param), reverse=True)
    return params


def _group_param_search(action, param_part: "zkau_", part_mode=True) -> iter(("zkau_5650", "zkau_5680",)):
    """поиск в action.c, всех param, в имени которых есть param_part / или по LB"""
    for web_ in action.web_action.get_web_snapshot_all():
        split_text = web_.get_body().split(param_part)

        for index in range(len(split_text) - 1):
            left = split_text[index].rsplit('\n', 1)[-1].lstrip()
            right = split_text[index + 1].split('\n', 1)[0].rstrip()

            if lr_lbrb_checker.check_bound_lb(left) if part_mode else (right[0] in lr_param.wrsp_allow_symb):
                param = []  # "5680"

                for s in right:
                    if s in lr_param.wrsp_allow_symb:
                        param.append(s)
                    else:
                        break

                if param:
                    param = ''.join(param)
                    if part_mode:  # param_part или по LB
                        param = param_part + param
                    yield param  # "zkau_5680"


@lr_vars.T_POOL_decorator
def re_auto_param_creator(action) -> None:
    """group params поиск, на основе регулярных выражений"""
    y = lr_dialog.YesNoCancel(['Найти', 'Отменить'], is_text='\n'.join(lr_vars.REGEXP_PARAMS), parent=action,
                              text_before='Будет произведен поиск param: re.findall(regexp, action_text)',
                              title='regexp {} шт.'.format(len(lr_vars.REGEXP_PARAMS)),
                              text_after='При необходимости - добавить/удалить')
    ans = y.ask()
    if ans == 'Найти':
        regexps = list(filter(bool, map(str.strip, y.text.split('\n'))))
    else:
        return

    def deny_params(lst: list) -> [str, ]:
        """удалить не param-слова"""
        for p in lst:
            check = ((p not in lr_vars.DENY_PARAMS) and (
                not (len(p) > 2 and p.startswith('on') and p[2].isupper()))) and (len(p) > 2)
            if check:
                for a in lr_vars.DENY_Startswitch_PARAMS:
                    if p.startswith(a):
                        check = not all(map(str.isnumeric, (p.split(a, 1)[1])))
                        break
                if check:
                    yield p

    params = []
    for r in regexps:
        prs = list(set(group_param_search_quotes(action, r=r)))
        prs = list(deny_params(prs))
        params.extend(prs)

    params = list(set(params))
    if params:
        params.sort(key=lambda param: len(param), reverse=True)
        y = lr_dialog.YesNoCancel(['создать', 'Отменить'], is_text='\n'.join(params), parent=action,
                                  text_before='Будет произведено создание param',
                                  title='param {} шт.'.format(len(params)),
                                  text_after='При необходимости - добавить/удалить')
        ans = y.ask()
        if ans == 'создать':
            params = list(filter(bool, map(str.strip, y.text.split('\n'))))
            group_param(None, widget=action.tk_text, params=params, ask=False)


def group_param_search_quotes(action, r=r'=(.+?)\"') -> iter((str,)):
    """поиск param, внутри кавычек"""

    def get_params() -> iter((str,)):
        for web_ in action.web_action.get_web_snapshot_all():
            params = re.findall(r, web_.get_body())
            yield from filter(bool, map(str.strip, params))

    for param in get_params():
        if all(map(lr_param.wrsp_allow_symb.__contains__, param)):  # не содержит неподходящих символов
            yield param