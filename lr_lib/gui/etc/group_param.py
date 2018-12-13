# -*- coding: UTF-8 -*-
# нахождение и замена group_param

import re
import sys
import queue

import tkinter as tk

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars as lr_vars


progress_str = '{proc}% : {counter}/{len_params} | fail={fail}\n{wrsp}'
final_str = '{state} | создано сейчас = {param} / fail={fail} : {unsuc} | всего {param_counter}'


@lr_vars.T_POOL_decorator
def group_param(event, widget=None, params=None, ask=True) -> None:
    """gui - нахождение и замена для группы web_reg_save_param's"""
    if widget is None:
        widget = event.widget

    params = _find_params(widget, params=params)
    if not params:
        lr_vars.Logger.warning('param не найдены! %s' % params, parent=widget.action)
        return

    len_params = _ask_params(params, widget.action, ask=ask)
    if not len_params:
        return

    # заменить params
    with lr_vars.Window.block(force=True), widget.action.block(), ProgressBar(len_params, widget) as progress_bar:
        widget.action.backup()
        for item in _group_param_iter(params, widget.action):  # заменить
            progress_bar(item)
            continue
    return


class ProgressBar:
    """рекурсивный асинхронный progressbar"""
    def __init__(self, len_params: int, widget):
        self.widget = widget
        self.len_params = len_params
        self.p1 = ((self.len_params / 100) or 1)

        item = (0, {'param': ''}, '', [])
        self.item0 = [item]  # [(counter, wrsp_dict, wrsp, unsuccess)]
        return

    def __enter__(self) -> 'callable':
        self.widget.action.show_hide_bar_1(force_show=True)
        self.start()
        return self.update

    def __exit__(self, exc_type, exc_val, exc_tb) -> tuple:
        self.stop()
        self.widget.action.show_hide_bar_1()
        return exc_type, exc_val, exc_tb

    def update(self, item: (int, dict, str, list)):
        """добавить данные для progressbar"""
        self.item0[:] = [item]
        return

    def start(self) -> None:
        """рекурсивный асинхронный progressbar"""
        lr_vars.MainThreadUpdater.submit(self._start)
        return

    def _start(self) -> None:
        """рекурсивный асинхронный progressbar"""
        (counter, wrsp_dict, wrsp, unsuccess) = self.item0[0]
        fail = len(unsuccess)

        if wrsp_dict:  # прогресс работы
            self.widget.action.toolbar['text'] = progress_str.format(
                counter=counter,
                len_params=self.len_params,
                fail=fail,
                proc=round(counter / self.p1),
                wrsp=wrsp,
            )
            # action цвет по кругу
            self.widget.action.background_color_set(color=None)
            # перезапуск с задержкой
            lr_vars.T_POOL.submit(self.start)
            return

        else:  # выход - результаты работы
            param_counter = self.widget.action.param_counter(all_param_info=False)
            self.widget.action.toolbar['text'] = final_str.format(
                state=str(not fail).upper(),
                param_counter=param_counter,
                fail=fail,
                unsuc=(', '.join(unsuccess) if fail else ''),
                param=(self.len_params - fail),
            )
            if unsuccess:
                lr_vars.Logger.error('{} param не были обработаны:\n\t{}'.format(
                    fail, '\n\t'.join(unsuccess)), parent=self.widget.action)

            self.widget.action.background_color_set(color='')  # action оригинальный цвет
            self.widget.action.set_combo_len()
            lr_vars.Logger.debug(param_counter)

            if self.widget.action.final_wnd_var.get():
                self.widget.action.legend()
        return

    def stop(self) -> None:
        """выход self.start"""
        item = list(self.item0[0])
        item[1] = None  # выход
        self.item0[:] = [item]
        return


def _find_params(widget, params: '(False or None)') -> [str, ]:
    """определить params из widget"""
    if params is None:  # поиск только по началу имени
        params = group_param_search(widget.action, widget.selection_get())
    elif params is False:  # поиск только по LB=
        params = session_params(widget.action, lb_list=[widget.selection_get()], ask=False)
    return params


def _ask_params(params: [str, ], action: 'lr_lib.gui.action.main_action.ActionWindow', ask=True) -> int:
    """спросить о создании params, -> 0 - не создавать"""
    old_len_params = len(params)
    if ask:
        pc = '{0} шт.'.format(old_len_params)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=['Найти', 'Отменить', 'Пропуск'], text_before='найти group param', text_after=pc,
            is_text='\n'.join(params), title=pc, parent=action, default_key='Найти')
        ask = y.ask()

        if ask == 'Найти':
            params = sorted(filter(bool, y.text.split('\n')), key=len, reverse=True)
        elif ask == 'Пропуск':
            params = []
        else:
            return 0

    new_len_params = len(params)
    lr_vars.Logger.info('Имеется {l} ранее созданных param.\nДля создания выбрано/найдено {p}/{_p} param.\n'.format(
        _p=old_len_params, p=new_len_params, l=len(action.web_action.websReport.wrsp_and_param_names)))
    return new_len_params


def _group_param_iter(params: [str, ],
                      action: 'lr_lib.gui.action.main_action.ActionWindow') -> iter((int, dict, str, [str, ]),):
    """ядро - найти и заменить группу web_reg_save_param"""
    unsuccess = []  # params, обработанные с ошибкой
    wrsp_dict_queue = queue.Queue()
    _thread_wrsp_dict_creator(wrsp_dict_queue, params, unsuccess, action)  # для param's, в фоне, создавать wrsp_dict's

    web_actions = tuple(action.web_action.get_web_snapshot_all())
    replace = action.web_action.replace_bodys_iter(web_actions)  # сопрограмма-заменить
    next(replace)
    try:

        for (counter, wrsp_dict) in enumerate(iter(wrsp_dict_queue.get, None), start=1):
            wrsp = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)

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
            wrsp_dicts.put_nowait(lr_vars.VarWrspDict.get())  # вернуть wrsp_dict
        except Exception:
            unsuccess.append(param)
            lr_lib.etc.excepthook.excepthook(*sys.exc_info())
        continue

    wrsp_dicts.put_nowait(None)  # exit
    return


@lr_vars.T_POOL_decorator
def auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """group params по кнопке PARAM - по LB + по началу имени"""
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        ['Найти', 'Отменить'], is_text='\n'.join(lr_vars.Params_names), parent=action,
        text_before='Будет произведен поиск param, имя которых начинается на указанные имена.',
        title='начало param-имен', text_after='При необходимости - добавить/удалить',
    )
    ans = y.ask()
    if ans == 'Найти':
        param_parts = list(filter(bool, map(str.strip, y.text.split('\n'))))

        params = set(session_params(action))  # поиск по LB=
        for part in param_parts:
            for param in group_param_search(action, part):
                params.add(param)  # поиск по началу имени
                continue
            continue

        params = [p for p in params if ((p not in lr_vars.DENY_PARAMS) and (
            not (len(p) > 2 and p.startswith('on') and p[2].isupper())))]
        params.sort(key=lambda param: len(param), reverse=True)

        y = lr_lib.gui.widj.dialog.YesNoCancel(
            ['Создать', 'Отменить'], is_text='\n'.join(params), parent=action,
            text_before='создание + автозамена. %s шт' % len(params), title='Имена param',
            text_after='При необходимости - добавить/удалить',
        )
        ans = y.ask()
        if ans == 'Создать':
            params = list(filter(bool, map(str.strip, y.text.split('\n'))))
            group_param(None, widget=action.tk_text, params=params, ask=False)
    return


def session_params(action: 'lr_lib.gui.action.main_action.ActionWindow', lb_list=None, ask=True) -> list:
    """поиск param в action, по LB="""
    if lb_list is None:
        lb_list = lr_vars.LB_PARAM_FIND_LIST

    if ask:
        text = action.tk_text.get(1.0, tk.END)
        lb_uuid = re.findall(r'uuid_\d=', text)
        lb_col_count = re.findall(r'p_p_col_count=\d&', text)

        text = '\n'.join(set(lb_list + lb_uuid + lb_col_count))
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=['Найти', 'Пропуск'], text_before='найти param по LB=', text_after='указать LB, с новой строки',
            is_text=text, title='автозамена по LB=', parent=action, default_key='Найти',
        )
        if y.ask() == 'Найти':
            lb_list = y.text.split('\n')
        else:
            return []

    params = []
    for p in filter(bool, lb_list):
        params.extend(_group_param_search(action, p, part_mode=False))
        continue

    i = list(reversed(sorted(p for p in set(params) if p not in lr_vars.DENY_PARAMS)))
    return i


def group_param_search(action: 'lr_lib.gui.action.main_action.ActionWindow',
                       param_part: "zkau_") -> ["zkau_5650", "zkau_5680", ]:
    """поиск в action.c, всех уникальных param, в имени которых есть param_part"""
    params = list(set(_group_param_search(action, param_part)))  # уникальных
    params.sort(key=lambda param: len(param), reverse=True)
    return params


def _group_param_search(action: 'lr_lib.gui.action.main_action.ActionWindow', param_part: "zkau_",
                        part_mode=True) -> iter(("zkau_5650", "zkau_5680",)):
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

            if lr_lib.core.etc.lbrb_checker.check_bound_lb(left) if part_mode else (
                    right[0] in lr_lib.core.wrsp.param.wrsp_allow_symb):
                param = []  # "5680"

                for s in right:
                    if s in lr_lib.core.wrsp.param.wrsp_allow_symb:
                        param.append(s)
                    else:
                        break
                    continue

                if param:
                    param = ''.join(param)
                    if part_mode:  # param_part или по LB
                        param = param_part + param
                    yield param  # "zkau_5680"
            continue
        continue
    return


@lr_vars.T_POOL_decorator
def re_auto_param_creator(action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """group params поиск, на основе регулярных выражений"""
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        ['Найти', 'Отменить'], is_text='\n'.join(lr_vars.REGEXP_PARAMS), parent=action,
        text_before='Будет произведен поиск param: re.findall(regexp, action_text)',
        title='regexp {} шт.'.format(len(lr_vars.REGEXP_PARAMS)), text_after='При необходимости - добавить/удалить',
    )
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
                    continue
                if check:
                    yield p
            continue
        return

    params = []
    for r in regexps:
        prs = list(set(group_param_search_quotes(action, r=r)))
        prs = list(deny_params(prs))
        params.extend(prs)
        continue

    params = list(set(params))
    if params:
        params.sort(key=lambda param: len(param), reverse=True)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            ['создать', 'Отменить'], is_text='\n'.join(params), parent=action,
            text_before='Будет произведено создание param', title='param {} шт.'.format(len(params)),
            text_after='При необходимости - добавить/удалить',
        )
        ans = y.ask()
        if ans == 'создать':
            params = list(filter(bool, map(str.strip, y.text.split('\n'))))
            group_param(None, widget=action.tk_text, params=params, ask=False)
    return


def group_param_search_quotes(action: 'lr_lib.gui.action.main_action.ActionWindow', r=r'=(.+?)\"') -> iter((str,)):
    """поиск param, внутри кавычек"""

    def get_params() -> iter((str,)):
        for web_ in action.web_action.get_web_snapshot_all():
            params = re.findall(r, web_.get_body())
            yield from filter(bool, map(str.strip, params))
            continue
        return

    for param in get_params():
        if all(map(lr_lib.core.wrsp.param.wrsp_allow_symb.__contains__, param)):  # не содержит неподходящих символов
            yield param
        continue
    return
