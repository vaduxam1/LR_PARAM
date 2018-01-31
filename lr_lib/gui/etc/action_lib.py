# -*- coding: UTF-8 -*-
# нахождение param и др команды из меню мыши, для gui

import json
import os
import re
import sys
import html
import queue
import codecs
import contextlib
import urllib.parse
import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.gui.etc.gui_other

import lr_lib.core.etc.other as lr_other
import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_func as lr_vars_func
import lr_lib.core.wrsp.param as lr_param
import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.gui.widj.dialog as lr_dialog


@lr_vars.T_POOL_decorator
def mouse_web_reg_save_param(widget, param, mode=('SearchAndReplace', 'highlight', ), wrsp=None, wrsp_dict=None, set_param=True) -> None:
    '''в окне action.c, для param, автозамена, залить цветом, установить виджеты'''
    action = widget.action

    with action.block():
        if 'SearchAndReplace' in mode:
            if not wrsp_dict:
                if set_param:
                    lr_vars.VarParam.set(param, action=action, set_file=True)
                    wrsp_dict = lr_param.wrsp_dict_creator()
                else:
                    wrsp_dict = lr_vars.VarWrspDict.get()

            # найти и заменить в action.c
            action.SearchAndReplace(search=param, wrsp_dict=wrsp_dict, is_param=True, is_wrsp=True, backup=True, wrsp=wrsp)

            w = wrsp_dict['web_reg_name']
            if lr_vars.VarShowPopupWindow.get() and action.final_wnd_var.get():
                action.search_in_action(word=w)
                s = '{wr}\n\n{wd}'.format(wr=action.web_action.websReport.param_statistic[w], wd=wrsp_dict)
                lr_vars.Logger.debug(s)
                tk.messagebox.showinfo(wrsp_dict['param'], s, parent=action)
                try:
                    action.search_res_combo.current(1)
                except tk.TclError:
                    action.search_res_combo.current(0)
                action.tk_text_see()

        elif 'highlight' in mode:
            highlight_mode(widget, param)
            action.tk_text.set_highlight()


@lr_vars.T_POOL_decorator
def rClick_Param(event, *args, **kwargs) -> None:
    '''web_reg_save_param из выделения, меню правой кнопки мыши'''
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
        widget = action.tk_text

    callback = lambda: mouse_web_reg_save_param(widget, param, *args, set_param=False, **kwargs)
    lr_vars.Window.get_files(param=param, callback=callback, action=action)


@lr_vars.T_POOL_decorator
def group_param(event, widget=None, params=None, ask=True) -> None:
    '''группа web_reg_save_param из выделения, меню правой кнопки мыши'''
    if widget is None:
        widget = event.widget
    action = widget.action

    if params is None:
        params = action.group_param_search(widget.selection_get())
    elif params is False:
        params = action.session_params(lb_list=[widget.selection_get()], ask=False)
    if not params:
        return lr_vars.Logger.warning('param не найдены! %s' % params, parent=action)

    len_params = len(params)
    lr_vars.Logger.info('для создания найдено {} param'.format(len_params))

    if ask:
        y = lr_dialog.YesNoCancel(
            buttons=['Найти', 'Отменить', 'Пропуск'], text_before='найти group param', text_after='%s шт.' % len_params,
            is_text='\n'.join(params), title='group param', parent=action, default_key='Найти')
        ask = y.ask()
        if ask == 'Найти':
            params = sorted(filter(bool, y.text.split('\n')), key=len, reverse=True)
        elif ask == 'Пропуск':
            params = []
        else:
            return

    lr_vars.Logger.debug('на текущий момент уже создано {} param'.format(len(action.web_action.websReport.wrsp_and_param_names)))
    lr_vars.Logger.info('>>> для создания выбрано {} param'.format(len_params))

    unsuccess_params = []  # param обработанные с ошибкой
    wrsp_dict_queue = queue.Queue()

    thread_wrsp_dict_creator(wrsp_dict_queue, params, unsuccess_params, action)  # создавать wrsp_dicts
    p1 = ((len_params / 100) or 1)
    progress = lambda: progress_group_param(counter, wrsp_dict['param'], p1, wrsp, unsuccess_params, len_params, action)

    replace_list = []  # [('aFFXt', '{P_9882_4_Window_main_a_FFX_t}'), ('aFFX9', '{P_3768_1_Window_login_a_FFX_9}')]
    action.backup()

    with lr_vars.Window.block(), action.block():
        lr_vars.Window._block_ = True

        for counter, wrsp_dict in enumerate(iter(wrsp_dict_queue.get, None), start=1):
            lr_vars.MainThreadUpdater.submit(progress)
            wrsp_name = lr_param.param_bounds_setter(wrsp_dict['web_reg_name'])
            wrsp = lr_param.create_web_reg_save_param(wrsp_dict)
            with contextlib.suppress(Exception): action.param_inf_checker(wrsp_dict, wrsp)

            replace_list.append((wrsp_dict['param'], wrsp_name))
            action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)  # вставить web_reg_save_param

        action.web_action.replace_bodys(replace_list)  # заменить
        action.web_action_to_tk_text(websReport=True)  # вставить в action.c
        lr_vars.Window._block_ = False

    lr_vars.MainThreadUpdater.submit(lambda: final_group_param(widget, unsuccess_params=unsuccess_params, log=True))


def progress_group_param(counter: int, param: str, proc1: int, wrsp: str, unsuccess_params: [str,], len_params: int, action) -> None:
    '''прогресс group_param()'''
    lu = len(unsuccess_params)
    u = (' | fail: %s' % lu if lu else '')
    t = '{param} : web_reg_save_param : {counter}/{len_params} : {w} %{u}\n{wrsp}'.format(
        counter=counter, len_params=len_params, u=u, w=round(counter / proc1), param=param, wrsp=wrsp)
    action.toolbar['text'] = t
    action.background_color_set(color=None)


@lr_vars.T_POOL_decorator
def thread_wrsp_dict_creator(wrsp_dict_queue, params, unsuccess_params, action) -> None:
    '''создать wrsp_dicts в потоке, чтобы не терять время, при показе popup окон'''
    for param in params:
        try:
            lr_vars.VarParam.set(param, action=action, set_file=True)
            wrsp_dict_queue.put_nowait(lr_vars.VarWrspDict.get())
        except Exception:
            unsuccess_params.append(param)
            lr_excepthook.excepthook(*sys.exc_info())
    wrsp_dict_queue.put_nowait(None)  # stop


def final_group_param(widget, unsuccess_params=None, log=False) -> None:
    '''результаты работы group_param'''
    widget.action.set_combo_len()
    widget.action.background_color_set(color='')  # оригинальный цвет

    pl = widget.action.param_counter(all_param_info=False)
    widget.action.toolbar['text'] = pl

    if unsuccess_params:
        err = len(unsuccess_params)
        n = ('{} param не были созданы ! {}'.format(err, ', '.join(unsuccess_params)) if err else '')
        widget.action.toolbar['text'] = '{s} : {n}\n{pl}'.format(s=str(not err).upper(), pl=pl, n=n)
        lr_vars.Logger.error('{} param не были обработаны:\n\t{}\nтребуется пересоздание, с OFF чекбоксом\n'
                             '"ограничить max_inf"'.format(err, '\n\t'.join(unsuccess_params)), parent=widget.action)

    if widget.action.final_wnd_var.get():
        repA(widget)
    if log:
        lr_vars.Logger.debug(pl)


def repA(widget) -> None:
    '''отчет сокращенный'''
    rep = widget.action.web_action.websReport.all_in_one
    t = 'transac_len={}, param_len={}'.format(len(rep), len(widget.action.web_action.websReport.wrsp_and_param_names))
    y = lr_dialog.YesNoCancel(buttons=['OK'], text_before='repA', text_after='websReport.all_in_one',
                              is_text=get_json(rep), title=t, parent=widget.action)
    lr_vars.T_POOL_decorator(y.ask)()


def repB(widget, counter=None) -> None:
    '''отчет полный'''
    wr = widget.action.web_action.websReport
    if counter is None:
        counter = len(wr.wrsp_and_param_names)

    obj = [wr.wrsp_and_param_names, wr.rus_webs, wr.google_webs, wr.bad_wrsp_in_usage,
           widget.action.web_action.transactions.sub_transaction, wr.web_transaction_sorted,
           wr.param_statistic, wr.web_snapshot_param_in_count, wr.web_transaction]
    ao = ['wrsp_and_param_names', 'rus_webs', 'google_webs', 'bad_wrsp_in_usage', 'sub_transaction',
          'web_transaction_sorted', 'param_statistic', 'web_snapshot_param_in_count', 'web_transaction']
    tb = ' | '.join('{}:{}'.format(e, a) for e, a in enumerate(ao, start=1))
    st = '\n----\n'
    ta = ('\n\n' + st).join('{}:{}{}{}'.format(e, ao[e - 1], st, get_json(ob)) for e, ob in enumerate(obj, start=1))

    y = lr_dialog.YesNoCancel(buttons=['OK'], text_before=tb, text_after='{} шт'.format(counter),
                              is_text='\n\n{}'.format(ta), title='создано: {} шт.'.format(counter), parent=widget.action)
    lr_vars.T_POOL_decorator(y.ask)()
    lr_vars.Logger.trace('{}\n\n{}'.format(tb, ta))


def get_json(obj, indent=5):
    try:
        return json.dumps(obj, indent=indent)
    except Exception:
        return obj


def remove_web_reg_save_param_from_action(event, selection=None) -> None:
    '''удалить web_reg_save_param с w.param или w.name == selection'''
    if selection is None:
        selection = event.widget.selection_get()

    param = event.widget.action.web_action.web_reg_save_param_remove(selection)
    event.widget.action.web_action_to_tk_text(websReport=True)  # вставить в action.c

    if param:
        event.widget.action.search_in_action(word=param)


@lr_vars.T_POOL_decorator
def all_wrsp_dict_web_reg_save_param(event) -> None:
    '''все варианты создания web_reg_save_param'''
    selection = event.widget.selection_get()
    with contextlib.suppress(AttributeError):
        wrsp_and_param = event.widget.action.web_action.websReport.wrsp_and_param_names
        if selection in wrsp_and_param:
            selection = wrsp_and_param[selection]

    lr_vars.VarParam.set(selection, action=event.widget.action, set_file=True)
    lr_vars.VarWrspDictList.clear()

    wrsp_dict = lr_param.wrsp_dict_creator()
    if wrsp_dict:
        dt = [wrsp_dict, lr_param.create_web_reg_save_param(wrsp_dict)]
        lr_vars.VarWrspDictList.append(dt)
    else:
        return

    while True:
        try:
            lr_vars_func.next_3_or_4_if_bad_or_enmpy_lb_rb('поиск всех возможных wrsp_dict')
            wrsp_dict = lr_param.wrsp_dict_creator()
            if wrsp_dict:
                dt = [wrsp_dict, lr_param.create_web_reg_save_param(wrsp_dict)]
                lr_vars.VarWrspDictList.append(dt)
        except UserWarning:
            break
        except Exception:
            continue

    len_dl = len(lr_vars.VarWrspDictList)
    y = lr_dialog.YesNoCancel(buttons=['Заменить/Создать', 'Выйти'],
                              text_before='отображены все найденные варианты, которыми можно создать web_reg_save_param\n'
                                          'необходимо оставить только один вариант, удалив остальные.',
                              text_after=('итого %s вариантов.' % len_dl), is_text='\n\n'.join(w[1] for w in lr_vars.VarWrspDictList),
                              title='{} : {} шт.'.format(selection, len_dl), parent=event.widget.action, default_key='Заменить/Создать')
    ask = y.ask()

    if ask == 'Заменить/Создать':
        remove_web_reg_save_param_from_action(event, selection=selection)
        user_wrsp = y.text.strip('\n')
        _wrsp = user_wrsp.strip()
        for wrsp_dict, wrsp in lr_vars.VarWrspDictList:
            if _wrsp == wrsp.strip():
                return mouse_web_reg_save_param(event.widget, selection, wrsp=user_wrsp, wrsp_dict=wrsp_dict)


@lr_vars.T_POOL_decorator
def rClick_web_reg_save_param_regenerate(event, new_lb_rb=True) -> None:
    '''из выделения, переформатировать LB/RB в уже созданном web_reg_save_param, меню правой кнопки мыши'''
    selection = event.widget.selection_get()
    try:
        action = event.widget.action
    except:
        action = next(iter(lr_vars.Window.action_windows.values()))

    if lr_param.wrsp_lr_start not in selection:
        return tk.messagebox.showwarning(str(rClick_web_reg_save_param_regenerate),
                                         'Ошибка, необходимо выделять весь блок, созданного web_reg_save_param, вместе с комментариями\n'
                                         'Сейчас "{wr}" не содержится в выделенном тексте:\n{selection}'.format(
                                             wr=lr_param.wrsp_lr_start, selection=selection[:1000]), parent=action)

    file_name = selection.split(lr_param.wrsp_file_start, 1)[-1]
    file_name = file_name.split(lr_param.wrsp_file_end, 1)[0]

    param = selection.split(lr_param.wrsp_start, 1)[-1]
    param = param.split(lr_param.wrsp_end, 1)[0]
    lr_vars.VarParam.set(param, action=action, set_file=False)  # найти
    lr_vars.VarFileName.set(file_name)

    sel = selection.split(lr_param.wrsp_lr_start, 1)[-1]
    sel = sel.split(lr_param.wrsp_lr_end, 1)
    wrsp_name, sel = sel[0], sel[-1]

    if new_lb_rb:  # сохранить LB/RB
        wrsp_lb = sel.split(lr_param.wrsp_LB_start, 1)[-1]
        wrsp_lb = wrsp_lb.split(lr_param.wrsp_LB_end, 1)[0]
        wrsp_rb = sel.split(lr_param.wrsp_RB_start, 1)[-1]
        wrsp_rb = wrsp_rb.split(lr_param.wrsp_RB_end, 1)[0]
        lr_vars.VarLB.set(value=wrsp_lb)
        lr_vars.VarRB.set(value=wrsp_rb)

    wrsp_dict = lr_param.wrsp_dict_creator()  # сформировать wrsp_dict
    wrsp_dict['web_reg_name'] = wrsp_name  # сохранить старое имя
    web_reg_save_param = lr_param.create_web_reg_save_param(wrsp_dict)  # создать

    txt = event.widget.get(1.0, tk.END).replace(selection, web_reg_save_param)
    action.backup()
    event.widget.delete(1.0, tk.END)
    event.widget.insert(1.0, txt)  # вставить
    action.save_action_file(file_name=False)
    action.search_in_action(word=wrsp_name)


def rClick_max_inf(event) -> None:
    '''max inf widget из выделения, меню правой кнопки мыши'''
    selection = event.widget.selection_get()
    m = re.sub("\D", "", selection)
    lr_vars.VarSearchMaxSnapshot.set(int(m))


def rClick_min_inf(event) -> None:
    '''min inf widget из выделения, меню правой кнопки мыши'''
    selection = event.widget.selection_get()
    m = re.sub("\D", "", selection)
    lr_vars.VarSearchMinSnapshot.set(int(m))


def rClick_Search(event) -> None:
    '''поиск выделения в тексте, меню правой кнопки мыши'''
    selection = event.widget.selection_get()
    with contextlib.suppress(AttributeError):
        event.widget.action.search_in_action(word=selection)


@lr_vars.T_POOL_decorator
def rename_transaction(event, parent=None, s='lr_start_transaction("', e='lr_end_transaction("') -> None:
    '''переименование транзакции - необходимо выделять всю линию с транзакцией'''
    selection = event.widget.selection_get().strip()
    try:
        old_name = selection.split(s, 1)[1].split('"', 1)[0]
    except IndexError:
        old_name = selection.split(e, 1)[1].split('"', 1)[0]

    if not parent:
        with contextlib.suppress(AttributeError):
            parent = event.widget.action

    y = lr_dialog.YesNoCancel(['Переименовать', 'Отмена'], 'Переименовать выделенную(линию) transaction',
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

        event.widget.action.backup()
        event.widget.delete(1.0, tk.END)
        event.widget.insert(1.0, '\n'.join(lit))  # вставить
        event.widget.action.save_action_file(file_name=False)


@lr_vars.T_POOL_decorator
def encoder(event, action=None) -> None:
    '''декодирование выделения'''
    try:
        widget = event.widget
    except AttributeError:
        widget = event
    if not action:
        with contextlib.suppress(AttributeError):
            action = widget.action

    selection = widget.selection_get().strip()

    combo_dict = {
        'cp1251': lambda: selection.encode('cp1251').decode(errors='replace'),
        'utf-8': lambda: selection.encode('utf-8').decode(errors='replace'),
        'unquote': lambda: urllib.parse.unquote(selection),
        'unescape': lambda: html.unescape(selection),
        'unicode_escape': lambda: codecs.decode(selection, 'unicode_escape', errors='replace'),
    }

    parent = (action or widget)
    y = lr_dialog.YesNoCancel(['заменить', 'Отмена'], 'декодер выделения', 'encode', 'decode', parent=parent,
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


def highlight_mode(widget, word: str, option='foreground', color='olive') -> None:
    '''залить цветом все word в tk.Text widget'''
    colors = widget.highlight_dict.setdefault(option, {})

    try:
        colors[color].add(word)
    except (KeyError, AttributeError):
        colors[color] = {word}


def add_highlight_words_to_file(event) -> None:
    '''сохранить слово для подсветки в файл - "навсегда" '''
    selection = event.widget.selection_get()

    with open(lr_vars.highlight_words_main_file, 'a') as f:
        f.write(selection + '\n')

    rClick_add_highlight(event, 'foreground', 'olive', 'добавить', find=True)


def rClick_add_highlight(event, option: str, color: str, val: str, find=False) -> None:
    '''для выделения, добавление color в highlight_dict, меню правой кнопки мыши'''
    try:
        hd = event.widget.highlight_dict
    except AttributeError:
        return

    selection = event.widget.selection_get()

    if val == 'добавить':
        highlight_mode(event.widget, selection, option, color)
    else:
        with contextlib.suppress(KeyError):
            hd[option][color].remove(selection)

    event.widget.action.save_action_file(file_name=False)
    if find:
        event.widget.action.search_in_action(word=selection)
        event.widget.action.tk_text_see()


def snapshot_files(event, folder='', i_num=0) -> None:
    '''показать окно файлов snapshot'''
    selection = event.widget.selection_get()
    if not folder:
        folder = lr_vars.VarFilesFolder.get()
    if not i_num:
        i_num = ''.join(filter(str.isnumeric, selection))

    top = tk.Toplevel()
    top.transient(event.widget)
    top.title('окно файлов snapshot=t{i}.inf'.format(i=i_num))
    lr_lib.gui.etc.gui_other.center_widget(top)

    def get_files_names(folder: str, i_num: int) -> iter((str,)):
        '''имена файлов'''
        fi = os.path.join(folder, 't{}.inf'.format(i_num))
        if not os.path.isfile(fi):
            return

        with open(fi) as inf:
            for line in inf:
                ls = line.strip()
                if 'File' in ls:
                    sls = ls.split('=', 1)
                    if len(sls) == 2:
                        yield sls[1]

    def widj(folder: str, i_num: int, tt='', mx=40) -> None:
        '''виджеты'''
        lab = tk.Label(top, text='{t}\n{f}'.format(t=tt, f=folder))
        fEntry = ttk.Combobox(top, justify='center', foreground='grey', background=lr_vars.Background,
                              font=lr_vars.DefaultFont + ' italic')
        files = list(get_files_names(folder, i_num))
        if not files:
            return

        fEntry['values'] = files

        m = max(map(len, fEntry['values']))
        if m < mx:
            m = mx
        fEntry.config(width=m)

        fEntry.bind("<<ComboboxSelected>>", lambda *a, e=fEntry: lr_other._openTextInEditor(os.path.join(folder, e.get())))
        lr_tooltip.createToolTip(fEntry, '{t}\n{f}'.format(t=tt, f=folder))

        lab.pack()
        fEntry.pack()

    widj(folder, i_num, tt='файлы при записи')
    folder = event.widget.action.get_result_folder()
    widj(folder, i_num, tt='файлы при воспроизведении')
