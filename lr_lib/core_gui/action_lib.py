# -*- coding: UTF-8 -*-
# команды из меню мыши

import os
import re
import html
import codecs
import urllib.parse

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars_core
import lr_lib.core.action.web_
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_other
import lr_lib.gui.widj.responce_files
import lr_lib.core.var.vars as lr_vars
from lr_lib.core.var import vars as lr_vars


@lr_lib.core.var.vars_other.T_POOL_decorator
def mouse_web_reg_save_param(widget: lr_lib.gui.widj.highlight_text.HighlightText, param: str,
                             mode=('SearchAndReplace', 'highlight', ), wrsp=None, wrsp_dict=None, set_param=True) -> None:
    """в окне action.c, для param, автозамена, залить цветом, установить виджеты"""
    with widget.action.block():
        if 'SearchAndReplace' in mode:
            if not wrsp_dict:
                if set_param:
                    lr_vars.VarParam.set(param, action=widget.action, set_file=True)
                    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
                else:
                    wrsp_dict = lr_vars.VarWrspDict.get()

            # найти и заменить в action.c
            widget.action.SearchAndReplace(search=param, wrsp_dict=wrsp_dict, is_wrsp=True, backup=True, wrsp=wrsp)

            w = wrsp_dict['web_reg_name']
            if lr_vars.VarShowPopupWindow.get() and widget.action.final_wnd_var.get():
                widget.action.search_in_action(word=w)
                s = '{wr}\n\n{wd}'.format(wr=widget.action.web_action.websReport.param_statistic[w], wd=wrsp_dict)
                lr_vars.Logger.debug(s)
                tk.messagebox.showinfo(wrsp_dict['param'], s, parent=widget.action)

                def callback() -> None:
                    """callback - тк search_in_action почемуто асинхронно вызывается.
                    переход на первый созданный [param}"""
                    try:
                        widget.action.search_res_combo.current(1)
                    except tk.TclError:
                        widget.action.search_res_combo.current(0)
                    widget.action.tk_text_see()
                    return

                lr_vars.MainThreadUpdater.submit(callback)

        elif 'highlight' in mode:
            widget.action.tk_text.highlight_mode(param)
            widget.action.tk_text.highlight_apply()
    return


@lr_lib.core.var.vars_other.T_POOL_decorator
def rClick_Param(event, *args, **kwargs) -> None:
    """web_reg_save_param из выделения, меню правой кнопки мыши, с отображением в виджетах lr_vars.Window окна"""
    widget = event.widget

    try:
        param = widget.selection_get()
        # print('индекс(tk.Text) начала выделения')
        # count = widget.count("1.0", "sel.first")
        # print(count)
    except tk.TclError:
        return lr_vars.Logger.warning('сбросилось выделение текста\ntry again', parent=widget)
    try:
        action = widget.action
    except AttributeError:
        action = lr_vars.Window.get_main_action()
        widget = action.tk_text  # lr_lib.gui.widj.highlight_text.HighlightText

    callback = lambda: mouse_web_reg_save_param(widget, param, *args, set_param=False, **kwargs)
    lr_vars.Window.get_files(param=param, callback=callback, action=action)
    return


def remove_web_reg_save_param_from_action(event, selection=None, find=True) -> None:
    """удалить web_reg_save_param с w.param или w.name == selection"""
    if selection is None:
        selection = event.widget.selection_get()

    param = event.widget.action.web_action.web_reg_save_param_remove(selection)
    event.widget.action.web_action_to_tk_text(websReport=True)  # вставить в action.c

    if find and param:
        event.widget.action.search_in_action(word=param)
    return


def event_action_getter(event):
    """если передали не event.widget.'action', то найти action"""
    try:
        action = event.widget.action
    except AttributeError:
        action = lr_vars.Window.get_main_action()

    return action


def rClick_max_inf(event) -> None:
    """max inf widget из выделения, меню правой кнопки мыши"""
    selection = event.widget.selection_get()
    m = re.sub("\D", "", selection)
    lr_vars.VarSearchMaxSnapshot.set(int(m))
    return


def rClick_min_inf(event) -> None:
    """min inf widget из выделения, меню правой кнопки мыши"""
    selection = event.widget.selection_get()
    m = re.sub("\D", "", selection)
    lr_vars.VarSearchMinSnapshot.set(int(m))
    return


def rClick_Search(event) -> None:
    """поиск выделения в тексте, меню правой кнопки мыши"""
    selection = event.widget.selection_get()
    try:
        event.widget.action.search_in_action(word=selection)
    except AttributeError as ex:
        pass
    return


@lr_lib.core.var.vars_other.T_POOL_decorator
def encoder(event, action=None) -> None:
    """декодирование выделения"""
    try:
        widget = event.widget
    except AttributeError:
        widget = event
    if not action:
        try:
            action = widget.action
        except AttributeError as ex:
            pass

    selection = widget.selection_get().strip()

    combo_dict = {
        'cp1251': lambda: selection.encode('cp1251').decode(errors='replace'),
        'utf-8': lambda: selection.encode('utf-8').decode(errors='replace'),
        'unquote': lambda: urllib.parse.unquote(selection),
        'unescape': lambda: html.unescape(selection),
        'unicode_escape': lambda: codecs.decode(selection, 'unicode_escape', 'replace'),
    }

    parent = (action or widget)
    y = lr_lib.gui.widj.dialog.YesNoCancel(['заменить', 'Отмена'], 'декодер выделения', 'encode', 'decode', parent=parent,
                                           is_text=selection, combo_dict=combo_dict)
    if y.ask() == 'заменить':
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
    """сохранить слово для подсветки в файл - "навсегда" """
    selection = event.widget.selection_get()

    with open(lr_lib.core.var.vars_highlight.highlight_words_main_file, 'a') as f:
        f.write(selection + '\n')

    rClick_add_highlight(event, 'foreground', lr_lib.core.var.vars_highlight.DefaultColor, 'добавить', find=True)
    return


def rClick_add_highlight(event, option: str, color: str, val: str, find=False) -> None:
    """для выделения, добавление color в highlight_dict, меню правой кнопки мыши"""
    try:
        hd = event.widget.highlight_dict
    except AttributeError:
        return

    selection = event.widget.selection_get()

    if val == 'добавить':
        event.widget.action.tk_text.highlight_mode(selection, option, color)
    else:
        try:
            hd[option][color].remove(selection)
        except KeyError as ex:
            pass

    event.widget.action.save_action_file(file_name=False)
    if find:
        event.widget.action.search_in_action(word=selection)
        event.widget.action.tk_text_see()
    return


def snapshot_files(widget: lr_lib.gui.widj.highlight_text.HighlightText, folder_record='', i_num=0, selection='') -> None:
    """показать окно файлов snapshot"""
    if not folder_record:
        folder_record = lr_vars.VarFilesFolder.get()
    folder_response = widget.action.get_result_folder()

    if not i_num:
        if not selection:
            selection = widget.selection_get()
        i_num = ''.join(filter(str.isnumeric, selection))

    lr_lib.gui.widj.responce_files.RespFiles(widget, i_num, folder_record, folder_response)
    return


def file_from_selection(event) -> str:
    """открыть файл из выделения"""
    selection = event.widget.selection_get()
    folder = lr_vars.VarFilesFolder.get()
    full_name = os.path.join(folder, selection)

    if os.path.isfile(full_name):
        lr_lib.core.etc.other._openTextInEditor(full_name)
    else:
        lr_vars.Logger.warning(
            'файл не найден :\n"{}" : len={}\n{}'.format(selection, len(selection), full_name), log=False)

    return full_name


def snapshot_text_from_selection(event) -> int:
    """открыть текст snapshot из выделения"""
    action = event_action_getter(event)
    selection = event.widget.selection_get()
    inf = int(''.join(filter(str.isnumeric, selection)))
    web_ = next(action.web_action.get_web_snapshot_by(snapshot=inf), None)

    if web_ is None:
        lr_vars.Logger.warning(
            'web_.snapshot не найден :\n"{}" : len={}\n{}'.format(selection, len(selection), inf), log=False)
    else:
        lr_lib.core.etc.other.openTextInEditor(web_.to_str(_all_stat=True))

    return inf


def wrsp_text_from_selection(event) -> object:
    """открыть текст wrsp из выделения"""
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
        wrsp = next(action.web_action.get_web_reg_save_param_by(name=selection), None)

    if wrsp is None:
        lr_vars.Logger.warning(
            'wrsp не найден :\n"{}" : len={}\n{}'.format(selection, len(selection), action), log=False)
    else:
        lr_lib.core.etc.other.openTextInEditor(wrsp.to_str(_all_stat=True))

    return wrsp


@lr_lib.core.var.vars_other.T_POOL_decorator
def rClick_web_reg_save_param_regenerate(event, new_lb_rb=True, selection=None, replace=True) -> (dict, str):
    """из выделения, переформатировать LB/RB в уже созданном web_reg_save_param, меню правой кнопки мыши"""
    if selection is None:
        selection = event.widget.selection_get()
    try:
        action = event.widget.action
    except:
        action = next(iter(lr_vars.Window.action_windows.values()))

    if lr_lib.core.wrsp.param.wrsp_lr_start not in selection:
        return tk.messagebox.showwarning(
            str(rClick_web_reg_save_param_regenerate),
            'Ошибка, необходимо выделять весь блок, созданного web_reg_save_param, вместе с комментариями\n'
            'Сейчас "{wr}" не содержится в выделенном тексте:\n{selection}'.format(
                wr=lr_lib.core.wrsp.param.wrsp_lr_start, selection=selection[:1000]), parent=action)

    file_name = selection.split(lr_lib.core.wrsp.param.wrsp_file_start, 1)[-1]
    file_name = file_name.split(lr_lib.core.wrsp.param.wrsp_file_end, 1)[0]

    param = selection.split(lr_lib.core.wrsp.param.wrsp_start, 1)[-1]
    param = param.split(lr_lib.core.wrsp.param.wrsp_end, 1)[0]
    lr_vars.VarParam.set(param, action=action, set_file=False)  # найти
    lr_vars.VarFileName.set(file_name)

    sel = selection.split(lr_lib.core.wrsp.param.wrsp_lr_start, 1)[-1]
    sel = sel.split(lr_lib.core.wrsp.param.wrsp_lr_end, 1)
    wrsp_name, sel = sel[0], sel[-1]

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
            txt = event.widget.get(1.0, tk.END).replace(selection, web_reg_save_param)
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
            action.web_action.replace_bodys([(wrsp_dict['param'], wrsp_name)])  # заменить в телах web's
            action.web_action_to_tk_text(websReport=True)  # вставить в action.c

            action.search_in_action(word=wrsp_name)

    return wrsp_dict, web_reg_save_param