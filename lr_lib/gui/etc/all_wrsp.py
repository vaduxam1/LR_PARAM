# -*- coding: UTF-8 -*-
# все варианты создания web_reg_save_param

import lr_lib
import lr_lib.core
import lr_lib.etc.excepthook
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.action_lib import event_action_getter


@lr_vars.T_POOL_decorator
def all_wrsp_dict_web_reg_save_param(event, wrsp_web_=None) -> None:
    """все варианты создания web_reg_save_param, искать не ограничивая верхний номер Snapshot"""
    action = event_action_getter(event)
    m = action.max_inf_cbx_var.get()
    action.max_inf_cbx_var.set(0)
    selection = event.widget.selection_get()

    with action.block():
        try:
            _all_wrsp_dict_web_reg_save_param(action, selection)
        except Exception as ex:
            lr_lib.etc.excepthook.excepthook(ex)
        finally:
            action.max_inf_cbx_var.set(m)

        if wrsp_web_:
            action.search_in_action(word=wrsp_web_.to_str())
    return


def _all_wrsp_dict_web_reg_save_param(action: 'lr_lib.gui.action.main_action.ActionWindow', selection: str) -> None:
    """все варианты создания web_reg_save_param"""
    try:
        wrsp_and_param = action.web_action.websReport.wrsp_and_param_names
    except AttributeError as ex:
        pass
    else:
        if selection in wrsp_and_param:  # сменить wrsp-имя в ориг. имя param
            param = wrsp_and_param[selection]
        else:
            param = selection

    lr_vars.VarParam.set(param, action=action, set_file=True)

    lr_vars.VarWrspDictList.clear()
    lr_vars.VarWrspDictList.extend(filter(_check_wrsp_duplicate, _all_wrsp(action)))
    assert lr_vars.VarWrspDictList, 'Ничего не найдено'

    param = lr_vars.VarWrspDictList[0][0]['param']
    answ_text = _ask_wrsp_create(param, action)
    if isinstance(answ_text, str):
        _create_wrsp_web_(answ_text, param, action)
    return


def _check_wrsp_duplicate(wr: (dict, str), dups=None) -> bool:
    """проверить, не создан ли ранее, такой же wrsp. False - создан, те дубликат."""
    wrsp = _wrsp_text_delta_remove(wr)
    if dups is None:
        dups = lr_vars.VarWrspDictList

    duplicate = any((wrsp == w) for w in map(_wrsp_text_delta_remove, dups))
    return not duplicate


def _wrsp_text_delta_remove(wr: (dict, str), ) -> str:
    """убрать 'вариативную' часть wrsp текста"""
    (wrsp_dict, wrsp) = wr
    delta = wrsp_dict['web_reg_name']
    without_delta = wrsp.replace(delta, '').strip()
    return without_delta


import queue
import threading


class ColorProgress:
    """
    менять цвет action.c окна при "работе" поиска всех вариантов создания web_reg_save_param
    """
    def __init__(self, action: 'lr_lib.gui.action.main_action.ActionWindow', start=False):
        self.is_work = [True]
        self.action = action

        if start:
            self.start(wait=0)
        return

    def stop(self) -> None:
        """остановка"""
        self.is_work.clear()
        return

    def start(self, wait=lr_vars._MTUT) -> None:
        """циклическая смена цвета"""
        t = threading.Timer(wait, self._start)
        t.start()
        return

    def _start(self) -> None:
        """циклическая смена цвета"""
        if self.is_work:
            self.color_change(None)  # смена
            self.start()  # рекурсия
            return
        else:
            self.color_change('')  # оригинальный цвет
        return

    def color_change(self, color: 'None or ""') -> None:
        """смена цвета"""
        fn = lambda: self.action.background_color_set(color=color)
        lr_vars.MainThreadUpdater.submit(fn)  # action цвет
        return


def _all_wrsp(action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """поиск всех возможных wrsp"""
    colors = ColorProgress(action, start=True)
    try:
        wr = _wr_create()  # первый/текущий wrsp
        while wr:
            yield wr
            wr = _next_wrsp()  # остальные wrsp
            continue
    finally:
        colors.stop()
    return


def _next_wrsp() -> 'iter([dict, str]) or None':
    """поиск следующего возможного wrsp"""
    try:
        lr_lib.core.var.vars_func.next_3_or_4_if_bad_or_enmpy_lb_rb('поиск всех возможных wrsp_dict')
    except UserWarning as ex:
        return  # конец поиска
    else:
        wr = _wr_create()
    return wr


def _wr_create() -> [dict, str]:
    """создание wrsp"""
    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
    wrsp_text = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)
    wr = [wrsp_dict, wrsp_text]
    return wr


text_after = '''Либо оставить только один web_reg_save_param, удалив остальные.
Либо оставить любое кол-во, при этом, у всех web_reg_save_param сменится имя - на имя первого создаваемого web_reg_save_param. 
Если создание происходит при уже существующем web_reg_save_param, сначала он будет удален, затем создан новый.'''

text_before = '''"{p}" используется {s} раз, в диапазоне snapshot-номеров [{mi}:{ma}].
Учитывать, что snapshot, в котором создается первый web_reg_save_param, должен быть меньше,
snapshot первого использования "{p}".'''

Title = '"{s}":len={l} | Найдено {f} вариантов создания web_reg_save_param.'


def _ask_wrsp_create(param: str, action: 'lr_lib.gui.action.main_action.ActionWindow', ) -> 'str or None':
    """вопрос о создании wrsp, -> str создать, None - нет"""
    len_dl = len(lr_vars.VarWrspDictList)
    infs = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, param))
    if not infs:
        wrsp_and_param = action.web_action.websReport.wrsp_and_param_names
        if param in wrsp_and_param:  # сменить wrsp-имя в ориг. имя param
            infs = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, wrsp_and_param[param]))
        else:
            wp = {wrsp_and_param[k]: k for k in wrsp_and_param}
            if param in wp:
                infs = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, wp[param]))
    if not infs:
        infs = [-1]

    is_true_ask = 'Создать'
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=[is_true_ask, 'Выйти'], text_after=text_after, default_key='Выйти',
        text_before=text_before.format(s=len(infs), p=param, mi=min(infs), ma=max(infs)),
        is_text='\n\n'.join(w[1] for w in lr_vars.VarWrspDictList),
        title=Title.format(s=param, l=len(param), f=len_dl), parent=action,
    )
    ask = y.ask()

    if ask == is_true_ask:
        return y.text
    return None


Word = 'LAST);'


def _create_wrsp_web_(text: str, param: str, action: 'lr_lib.gui.action.main_action.ActionWindow') -> None:
    """создать в action web_reg_save_param"""
    action.backup()
    first_only = True  # если создается несколько wrsp_web_
    first_name = ''

    for part in text.split(Word):
        part = part.lstrip()
        if not part.rstrip():
            continue

        wrsp = (part + Word)
        # брать snapshot из камента
        s = wrsp.split(lr_lib.core.wrsp.param.SnapInComentS, 1)[1]
        s = s.split(lr_lib.core.wrsp.param.SnapInComentE, 1)[0]
        s = s.split(',', 1)[0]  # может быть несколько?
        snap = int(s)

        if first_only:
            action.web_action.web_reg_save_param_remove(param)  # удалить старый wrsp
        else:
            wrsp = _wrsp_name_replace(wrsp, first_name)

        # сохр wrsp в web
        wrsp_web_ = action.web_action.web_reg_save_param_insert(snap, wrsp)

        if first_only:
            p = (param, wrsp_web_.name)
            action.web_action.replace_bodys([p])  # заменить в телах web's
            first_name = wrsp_web_.name
            first_only = False

        continue

    # вставить в action.c
    action.web_action_to_tk_text(websReport=True)
    return


def _wrsp_name_replace(web_text: str, new_name: str) -> str:
    """замена имени wrsp, в wrsp тексте"""
    for line in web_text.split('\n'):
        if line.lstrip().startswith(lr_lib.core.wrsp.param.wrsp_lr_start):
            new_line = (lr_lib.core.wrsp.param.wrsp_lr_start + new_name + lr_lib.core.wrsp.param.wrsp_lr_end)
            return web_text.replace(line, new_line)
        continue

    lr_vars.Logger.debug('Ошибка замены имени wrsp "{n}" - не найдена web_reg_save_param линия.\n{t}'.format(
        n=new_name, t=web_text))
    return web_text
