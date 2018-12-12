# -*- coding: UTF-8 -*-
# команды из меню мыши

import os
import re
import html
import codecs
import urllib.parse

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars_func
import lr_lib.core.action.web_
import lr_lib.gui.widj.responce_files
import lr_lib.core.var.vars as lr_vars


@lr_vars.T_POOL_decorator
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


@lr_vars.T_POOL_decorator
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


@lr_vars.T_POOL_decorator
def all_wrsp_dict_web_reg_save_param(event, wrsp_web_=None) -> None:
    """все варианты создания web_reg_save_param, искать не ограничивая верхний номер Snapshot"""
    action = event_action_getter(event)
    m = action.max_inf_cbx_var.get()
    action.max_inf_cbx_var.set(0)
    selection = event.widget.selection_get()

    with action.block():
        try:
            for wrsp_web_ in filter(bool, _all_wrsp_dict_web_reg_save_param(action, selection)):
                continue
        finally:
            action.max_inf_cbx_var.set(m)

        if wrsp_web_:
            # action.tk_text_to_web_action(websReport=False)
            action.search_in_action(word=wrsp_web_.to_str())
    return


def _wrsp_text_delta_remove(wr: (dict, str), ) -> str:
    """убрать 'вариативную' часть wrsp текста"""
    (wrsp_dict, wrsp) = wr
    delta = wrsp_dict['web_reg_name']
    without_delta = wrsp.replace(delta, '').strip()
    return without_delta


def _check_wrsp_duplicate(wr: (dict, str), ) -> bool:
    """проверить, не создан ли ранее, такой же wrsp. True - создан, те дубликат."""
    wrsp = _wrsp_text_delta_remove(wr)
    duplicate = any((wrsp == w) for w in map(_wrsp_text_delta_remove, lr_vars.VarWrspDictList))
    return duplicate


def _all_wrsp_dict_web_reg_save_param(action: 'lr_lib.gui.action.main_action.ActionWindow',
                                      selection: str) -> iter((lr_lib.core.action.web_.WebRegSaveParam,)):
    """все варианты создания web_reg_save_param"""
    try:
        wrsp_and_param = action.web_action.websReport.wrsp_and_param_names
        if selection in wrsp_and_param:  # сменить wrsp-имя в ориг. имя param
            selection = wrsp_and_param[selection]
    except AttributeError as ex:
        pass

    lr_vars.VarParam.set(selection, action=action, set_file=True)
    lr_vars.VarWrspDictList.clear()

    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
    param = wrsp_dict['param']

    if wrsp_dict:
        dt = [wrsp_dict, lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)]
        lr_vars.VarWrspDictList.append(dt)
    else:
        return

    while True:
        try:
            lr_lib.core.var.vars_func.next_3_or_4_if_bad_or_enmpy_lb_rb('поиск всех возможных wrsp_dict')
            wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
            if wrsp_dict:
                wr = (wrsp_dict, lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict))
                if _check_wrsp_duplicate(wr):
                    continue
                lr_vars.VarWrspDictList.append(wr)
        except UserWarning:
            break
        except Exception:
            pass
        continue

    len_dl = len(lr_vars.VarWrspDictList)
    fl = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, param))
    if not fl:
        wrsp_and_param = action.web_action.websReport.wrsp_and_param_names
        if param in wrsp_and_param:  # сменить wrsp-имя в ориг. имя param
            fl = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, wrsp_and_param[param]))
        else:
            wp = {wrsp_and_param[k]: k for k in wrsp_and_param}
            if param in wp:
                fl = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, wp[param]))
    if not fl:
        fl = [-1]

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=['Создать', 'Выйти'],
        text_after='Либо оставить только один web_reg_save_param, удалив остальные.\n'
                   'Либо оставить любое кол-во, при этом, у всех web_reg_save_param сменится имя -\n\t'
                   '- на имя первого создаваемого web_reg_save_param.\n'
                   'Если создание происходит при уже существующем web_reg_save_param, '
                   'сначала он будет удален, затем создан новый.',
        text_before=('"{p}" используется {s} раз, в диапазоне snapshot-номеров [{mi}:{ma}].\n'
                     'Учитывать, что snapshot, в котором создается первый web_reg_save_param, должен быть меньше,\n'
                     'snapshot первого использования "{p}".'.format(
            s=len(fl), p=selection, mi=min(fl), ma=max(fl))),
        is_text='\n\n'.join(w[1] for w in lr_vars.VarWrspDictList),
        title='"{s}":len={l} | Найдено {f} вариантов создания web_reg_save_param.'.format(
            s=selection, l=len(selection), f=len_dl), parent=action,
        default_key='Выйти')
    ask = y.ask()

    if ask == 'Создать':
        action.backup()
        word = 'LAST);'
        text = y.text
        first_only = True  # если создается несколько wrsp_web_
        first_name = ''

        for part in text.split(word):
            part = part.lstrip()
            if not part.rstrip():
                continue

            wrsp = (part + word)
            # брать snapshot из камента
            s = wrsp.split(lr_lib.core.wrsp.param.SnapInComentS, 1)[1]
            s = s.split(lr_lib.core.wrsp.param.SnapInComentE, 1)[0]
            s = s.split(',', 1)[0]  # может быть несколько?
            snap = int(s)

            if first_only:
                action.web_action.web_reg_save_param_remove(selection)  # удалить старый wrsp
            else:
                wrsp = _wrsp_name_replace(wrsp, first_name)

            wrsp_web_ = action.web_action.web_reg_save_param_insert(snap, wrsp)  # сохр wrsp в web

            if first_only:
                action.web_action.replace_bodys([(param, wrsp_web_.name)])  # заменить в телах web's
                first_name = wrsp_web_.name
                first_only = False

            yield wrsp_web_
            continue

        action.web_action_to_tk_text(websReport=True)  # вставить в action.c
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


@lr_vars.T_POOL_decorator
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


@lr_vars.T_POOL_decorator
def rename_transaction(event, parent=None, s='lr_start_transaction("', e='lr_end_transaction("') -> None:
    """переименование транзакции - необходимо выделять всю линию с транзакцией"""
    selection = event.widget.selection_get().strip()
    try:
        old_name = selection.split(s, 1)[1].split('"', 1)[0]
    except IndexError:
        old_name = selection.split(e, 1)[1].split('"', 1)[0]

    if not parent:
        try:
            parent = event.widget.action
        except AttributeError as ex:
            pass

    y = lr_lib.gui.widj.dialog.YesNoCancel(['Переименовать', 'Отмена'], 'Переименовать выделенную(линию) transaction',
                              'указать только новое имя transaction', 'transaction', parent=parent, is_text=old_name)
    s1 = s + old_name
    s2 = e + old_name

    if y.ask() == 'Переименовать':
        new_name = y.text.strip()
        lit = event.widget.action.tk_text.get(1.0, tk.END).split('\n')
        for e, line in enumerate(lit):
            l = line.lstrip()
            if l.startswith(s1) or l.startswith(s2):
                lit[e] = line.replace(old_name, new_name)
            continue

        event.widget.action.backup()
        event.widget.delete(1.0, tk.END)
        event.widget.insert(1.0, '\n'.join(lit))  # вставить
        event.widget.action.save_action_file(file_name=False)
    return


@lr_vars.T_POOL_decorator
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

    with open(lr_vars.highlight_words_main_file, 'a') as f:
        f.write(selection + '\n')

    rClick_add_highlight(event, 'foreground', lr_vars.DefaultColor, 'добавить', find=True)
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


@lr_vars.T_POOL_decorator
def all_wrsp_auto_rename(gui: 'lr_lib.gui.action.main_action.ActionWindow', *a, ) -> None:
    """
    переименавать все wrsp, автоматически, с учетом всех настроек, для wrsp, содержащих LB/RB вида:
        ('"LB=', '"RB='), ('"LB/IC=', '"RB/IC=')
    например "JSESSIONID5" -> "P_6725_1__jsessionid__uJeCvxe"
    """
    _wrsps = tuple(gui.web_action.get_web_reg_save_param_all())
    wrsps = [w.name for w in _wrsps]

    get_bound = lambda line, spl: line.split(spl, 1)[1].rsplit('",', 1)[0]
    bounds = [('"LB=', '"RB='), ('"LB/IC=', '"RB/IC=')]

    wrsps_new = []
    lb = rb = ''

    # найти LR/RB из wrsp текста
    for w in _wrsps:
        for line in w.lines_list:
            line = line.strip()

            for (l_, r_) in bounds:
                if line.startswith(l_):
                    lb = get_bound(line, l_)
                elif line.startswith(r_):
                    rb = get_bound(line, r_)

                if lb and rb:
                    break
                continue
            continue

        if not (lb and rb):
            i = wrsps.index(w.name)
            del wrsps[i]
            continue
        new_name = lr_lib.core.wrsp.param.wrsp_name_creator(w.param, lb, rb, w.snapshot.inf)
        wrsps_new.append(new_name)
        continue

    mx = max(map(len, wrsps or ['']))
    m = '"{:<%s}" -> "{}"' % mx
    all_wrsps = '\n'.join(m.format(old, new) for (old, new) in zip(wrsps, wrsps_new))
    y = lr_lib.gui.widj.dialog.YesNoCancel(['Переименовать', 'Отмена'], 'Переименовать wrsp слева',
                              'в wrsp справа', 'wrsp',
                                           parent=gui, is_text=all_wrsps)

    if y.ask() == 'Переименовать':
        new_wrsps = [t.split('-> "', 1)[1].split('"', 1)[0].strip() for t in y.text.strip().split('\n')]
        assert len(wrsps) == len(new_wrsps)
        with gui.block():
            gui.backup()
            text = gui.tk_text.get('1.0', tk.END)

            for (old, new) in zip(wrsps, new_wrsps):
                text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old),
                                    lr_lib.core.wrsp.param.param_bounds_setter(new))
                text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old, start='"', end='"'),
                                    lr_lib.core.wrsp.param.param_bounds_setter(new, start='"', end='"'))
                continue

            gui.web_action.set_text_list(text, websReport=True)
            gui.web_action_to_tk_text(websReport=False)
    return

