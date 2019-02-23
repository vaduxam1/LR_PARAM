# -*- coding: UTF-8 -*-
# команды из меню мыши

import codecs
import functools
import html
import os
import re
import tkinter as tk
import urllib.parse
from typing import Iterable, Tuple, List, Callable

import lr_lib
import lr_lib.core.action.web_
import lr_lib.core.var.etc.init_vars
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars_highlight
import lr_lib.gui.widj.responce_files
from lr_lib.core.var import vars as lr_vars


def _block_decor(func: Callable) -> Callable:
    """декоратор widget.action.block - widget должен быть первым аргументом"""
    functools.wraps(func)

    def wrapper(widget: 'lr_lib.gui.widj.highlight_text.HighlightText', *args, **kwargs):
        with widget.action.block():
            out = func(widget, *args, **kwargs)
        return out

    return wrapper


@lr_lib.core.var.etc.vars_other.T_POOL_decorator
@_block_decor
def mouse_web_reg_save_param(
        widget: 'lr_lib.gui.widj.highlight_text.HighlightText',
        param: str,
        mode=('SearchAndReplace', 'highlight',),
        wrsp=None,
        wrsp_dict=None,
        set_param=True,
) -> None:
    """
    автозамена param в action.c, залить цветом, установить виджеты
    """
    action = widget.action

    if 'SearchAndReplace' in mode:
        if not wrsp_dict:
            if set_param:
                lr_vars.VarParam.set(param, action=action, set_file=True)
                wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
            else:
                wrsp_dict = lr_vars.VarWrspDict.get()

        # найти и заменить в action.c
        action.SearchAndReplace(search=param, wrsp_dict=wrsp_dict, is_wrsp=True, backup=True, wrsp=wrsp)

        popup = lr_vars.VarShowPopupWindow.get()
        final_wnd = action.final_wnd_var.get()
        if popup and final_wnd:
            w = wrsp_dict['web_reg_name']
            action.search_in_action(word=w)

            param_statistic = action.web_action.websReport.param_statistic[w]
            s = '{param_statistic}\n\n{wrsp_dict}'.format(param_statistic=param_statistic, wrsp_dict=wrsp_dict)
            p = wrsp_dict['param']
            lr_vars.Logger.debug(s)
            tk.messagebox.showinfo(p, s, parent=action)

            def callback() -> None:
                """callback тк search_in_action почемуто асинхронно вызывается + переход на первый созданный [param}"""
                try:
                    action.search_res_combo.current(1)
                except tk.TclError:
                    action.search_res_combo.current(0)
                action.tk_text_see()
                return

            lr_vars.MainThreadUpdater.submit(callback)

    elif 'highlight' in mode:
        action.tk_text.highlight_mode(param)
        action.tk_text.highlight_apply()
    return


@lr_lib.core.var.etc.vars_other.T_POOL_decorator
def rClick_Param(event, *args, **kwargs) -> None:
    """
    web_reg_save_param из выделения, меню правой кнопки мыши, с отображением в виджетах lr_vars.Window окна
    """
    widget = event.widget

    try:
        param = widget.selection_get()
        # print('индекс(tk.Text) начала выделения')
        # count = widget.count("1.0", "sel.first")
        # print(count)
    except tk.TclError:
        i = 'сбросилось выделение текста\ntry again'
        lr_vars.Logger.warning(i, parent=widget)
        return

    try:
        action = widget.action
    except AttributeError:
        action = lr_vars.Window.get_main_action()
        widget = action.tk_text  # lr_lib.gui.widj.highlight_text.HighlightText

    def callback() -> None:
        """автозамена param в action.c"""
        mouse_web_reg_save_param(widget, param, *args, set_param=False, **kwargs)
        return

    lr_vars.Window.get_files(param=param, callback=callback, action=action)
    return


def remove_web_reg_save_param_from_action(event, selection=None, find=True) -> None:
    """
    удалить web_reg_save_param с w.param или w.name == selection
    """
    if selection is None:
        selection = event.widget.selection_get()
    action = event_action_getter(event)

    param = action.web_action.web_reg_save_param_remove(selection)
    action.web_action_to_tk_text(websReport=True)  # вставить в action.c

    if find and param:
        action.search_in_action(word=param)
    return


def event_action_getter(event) -> 'lr_lib.gui.action.main_action.ActionWindow':
    """
    если передали не event.widget.'action', то найти action
    """
    try:
        action = event.widget.action
    except AttributeError:
        action = lr_vars.Window.get_main_action()

    return action


def rClick_max_inf(event) -> None:
    """
    max inf widget из выделения, меню правой кнопки мыши
    """
    selection = event.widget.selection_get()
    m = re.sub("\D", "", selection)
    m = int(m)
    lr_vars.VarSearchMaxSnapshot.set(m)
    return


def rClick_min_inf(event) -> None:
    """
    min inf widget из выделения, меню правой кнопки мыши
    """
    selection = event.widget.selection_get()
    m = re.sub("\D", "", selection)
    m = int(m)
    lr_vars.VarSearchMinSnapshot.set(m)
    return


def rClick_Search(event) -> None:
    """
    поиск выделения в тексте, меню правой кнопки мыши
    """
    selection = event.widget.selection_get()
    action = event_action_getter(event)
    action.search_in_action(word=selection)
    return


@lr_lib.core.var.etc.vars_other.T_POOL_decorator
def encoder(event, action=None) -> None:
    """
    декодирование выделения
    """
    try:
        widget = event.widget
    except AttributeError:
        widget = event
    if not action:
        try:
            action = widget.action
        except AttributeError:
            pass  # предназначено не для action виджета

    selection = widget.selection_get().strip()

    combo_dict = {
        'cp1251': lambda: selection.encode('cp1251').decode(errors='replace'),
        'utf-8': lambda: selection.encode('utf-8').decode(errors='replace'),
        'unquote': lambda: urllib.parse.unquote(selection),
        'unescape': lambda: html.unescape(selection),
        'unicode_escape': lambda: codecs.decode(selection, 'unicode_escape', 'replace'),
    }

    parent = (action or widget)
    key = 'заменить'
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=[key, 'Отмена'],
        text_before='декодер выделения',
        text_after='encode',
        title='decode',
        parent=parent,
        is_text=selection,
        combo_dict=combo_dict,
    )
    if y.ask() == key:
        new_name = y.text.strip()

        if action:
            txt = widget.action.tk_text.get(1.0, tk.END)
            widget.action.backup()
        else:
            txt = widget.get(1.0, tk.END)

        new_text = txt.replace(selection, new_name)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, new_text)  # вставить

        if action:
            widget.action.save_action_file(file_name=False)
            widget.action.search_in_action(word=new_name)
    return


def add_highlight_words_to_file(event) -> None:
    """
    сохранить слово для подсветки в файл - "навсегда"
    """
    selection = event.widget.selection_get().strip()
    selection += '\n'
    with open(lr_lib.core.var.vars_highlight.highlight_words_main_file, 'a') as f:
        f.write(selection)

    rClick_add_highlight(event, 'foreground', lr_lib.core.var.vars_highlight.DefaultColor, 'добавить', find=True)
    return


def rClick_add_highlight(event, option: str, color: str, val: str, find=False) -> None:
    """
    для выделения, добавление color в highlight_dict, меню правой кнопки мыши
    """
    selection = event.widget.selection_get()
    action = event_action_getter(event)

    if val == 'добавить':
        action.tk_text.highlight_mode(selection, option, color)
    else:  # удялять любые найденные для selection
        for option in action.tk_text.highlight_dict:
            c_dt = action.tk_text.highlight_dict[option]
            for color in c_dt:
                values = c_dt[color]  # <class 'set'>: {'mail.ru', '*/', 'yandex.ru', 'google.com', '/*', 'WARNING'}
                try:
                    values.remove(selection)  # удялить
                except KeyError:
                    pass
                continue
            continue

    action.save_action_file(file_name=False)
    if find:
        action.search_in_action(word=selection)
        action.tk_text_see()
    return


def snapshot_files(
        widget: 'lr_lib.gui.widj.highlight_text.HighlightText',
        folder_record='',
        i_num=0,
        selection='',
) -> None:
    """
    показать окно файлов snapshot
    """
    if not folder_record:
        folder_record = lr_vars.VarFilesFolder.get()
    folder_response = widget.action.get_result_folder()

    if not i_num:
        if not selection:
            selection = widget.selection_get()

        i = filter(str.isnumeric, selection)
        i_num = ''.join(i)

    lr_lib.gui.widj.responce_files.RespFiles(widget, i_num, folder_record, folder_response)
    return


def file_from_selection(event) -> str:
    """
    открыть файл из выделения
    """
    selection = event.widget.selection_get()
    folder = lr_vars.VarFilesFolder.get()
    full_name = os.path.join(folder, selection)

    if os.path.isfile(full_name):
        lr_lib.core.etc.other._openTextInEditor(full_name)
    else:
        len_selection = len(selection)
        i = 'файл не найден :\n"{selection}" : len={selection}\n{file_name}'
        i = i.format(selection, len_select=len_selection, file_name=full_name, )
        lr_vars.Logger.warning(i, log=False)

    return full_name


def snapshot_text_from_selection(event) -> int:
    """
    открыть текст snapshot из выделения
    """
    action = event_action_getter(event)
    selection = event.widget.selection_get()

    snapshot = filter(str.isnumeric, selection)
    snapshot = ''.join(snapshot)
    snapshot = int(snapshot)

    webs = action.web_action.get_web_snapshot_by(snapshot=snapshot)
    web_ = next(webs, None)

    if web_ is None:
        len_selection = len(selection)
        i = 'web_.snapshot не найден :\n"{selection}" : len={len_selection}\n{snapshot}'
        i = i.format(selection=selection, len_selection=len_selection, snapshot=snapshot, )
        lr_vars.Logger.warning(i, log=False)
    else:
        i = web_.to_str(_all_stat=True)
        lr_lib.core.etc.other.openTextInEditor(i)

    return snapshot


def wrsp_text_from_selection(event) -> object:
    """
    открыть текст wrsp из выделения
    """
    action = event_action_getter(event)
    selection = event.widget.selection_get()

    try:
        wrsp_and_param = action.web_action.websReport.wrsp_and_param_names
        if selection not in wrsp_and_param:  # сменить wrsp-имя в ориг. имя param
            wrsp_and_param = {wrsp_and_param[k]: k for k in wrsp_and_param}
            selection = wrsp_and_param[selection]
    except KeyError:
        wrsp = None
    else:
        w = action.web_action.get_web_reg_save_param_by(name=selection)
        wrsp = next(w, None)

    if wrsp is None:
        len_selection = len(selection)
        i = 'wrsp не найден :\n"{selection}" : len={len_selection}, id_={action}'
        i = i.format(selection=selection, len_selection=len_selection, action=action.id_, )
        lr_vars.Logger.warning(i, log=False)
    else:
        i = wrsp.to_str(_all_stat=True)
        lr_lib.core.etc.other.openTextInEditor(i)

    return wrsp


@lr_lib.core.var.etc.vars_other.T_POOL_decorator
def rClick_web_reg_save_param_regenerate(event, new_lb_rb=True, selection=None, replace=True) -> Tuple[dict, str]:
    """
    из выделения, переформатировать LB/RB в уже созданном web_reg_save_param, меню правой кнопки мыши
    """
    if selection is None:
        selection = event.widget.selection_get()

    action = event_action_getter(event)

    if lr_lib.core.wrsp.param.wrsp_lr_start not in selection:
        s = 'Ошибка, необходимо выделять весь блок, созданного web_reg_save_param, вместе с комментариями\n' \
            'Сейчас "{wrsp}" не содержится в выделенном тексте:\n{selection}'
        s = s.format(wrsp=lr_lib.core.wrsp.param.wrsp_lr_start, selection=selection[:1000])
        tk.messagebox.showwarning('изменить LB/RB в созданном web_reg_save_param', s, parent=action)
        return

    file_name = selection.split(lr_lib.core.wrsp.param.wrsp_file_start, 1)[-1]
    file_name = file_name.split(lr_lib.core.wrsp.param.wrsp_file_end, 1)[0]

    param = selection.split(lr_lib.core.wrsp.param.wrsp_start, 1)[-1]
    param = param.split(lr_lib.core.wrsp.param.wrsp_end, 1)[0]
    lr_vars.VarParam.set(param, action=action, set_file=False)  # найти
    lr_vars.VarFileName.set(file_name)

    sel = selection.split(lr_lib.core.wrsp.param.wrsp_lr_start, 1)[-1]
    sel = sel.split(lr_lib.core.wrsp.param.wrsp_lr_end, 1)
    (wrsp_name, sel) = (sel[0], sel[-1])

    if new_lb_rb:  # сохранить LB/RB
        _lb = sel.split(lr_lib.core.wrsp.param.wrsp_LB_start, 1)[-1]
        wrsp_lb = _lb.split(lr_lib.core.wrsp.param.wrsp_LB_end, 1)[0]
        lr_vars.VarLB.set(value=wrsp_lb)

        _rb = sel.split(lr_lib.core.wrsp.param.wrsp_RB_start, 1)[-1]
        wrsp_rb = _rb.split(lr_lib.core.wrsp.param.wrsp_RB_end, 1)[0]
        lr_vars.VarRB.set(value=wrsp_rb)

    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()  # сформировать wrsp_dict
    web_reg_save_param = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)  # создать

    if replace:  # заменить
        try:
            _ = event.widget.action
        except AttributeError:  # не  action
            t = event.widget.get(1.0, tk.END)
            txt = t.replace(selection, web_reg_save_param)
            event.widget.delete(1.0, tk.END)
            event.widget.insert(1.0, txt)  # вставить
        else:
            action.backup()
            action.web_action.web_reg_save_param_remove(param)  # удалить(при замене)
            try:
                action.param_inf_checker(wrsp_dict, web_reg_save_param)
            except Exception as ex:
                pass

            wrsp_name = wrsp_dict['web_reg_name']
            action.web_action.web_reg_save_param_insert(wrsp_dict, web_reg_save_param)  # сохр web_reg_save_param в web
            w = (wrsp_dict['param'], wrsp_name)
            action.web_action.replace_bodys([w, ])  # заменить в телах web's
            action.web_action_to_tk_text(websReport=True)  # вставить в action.c

            action.search_in_action(word=wrsp_name)

    it = (wrsp_dict, web_reg_save_param)
    return it
