# -*- coding: UTF-8 -*-
# разное для gui

import json
import re
import sys
import html
import queue
import codecs
import threading
import contextlib
import urllib.parse
import tkinter as tk
import tkinter.ttk as ttk

from lr_lib import (
    defaults,
    param as lr_param,
    pool as lr_pool,
    window_widj as lr_widj,
    var_setter as lr_setter,
    logger as lr_log,
)


@lr_pool.T_POOL_execute_decotator
def mouse_web_reg_save_param(widget, param, mode=('SearchAndReplace', 'highlight', ), wrsp=None, wrsp_dict=None,
                             set_param=True) -> None:
    '''в окне action.c, для param, автозамена, залить цветом, установить виджеты'''
    with widget.action.block():
        if 'SearchAndReplace' in mode:
            if not wrsp_dict:
                if set_param:
                    defaults.VarParam.set(param, action=widget.action, set_file=True)
                    wrsp_dict = lr_param.wrsp_dict_creator()
                else:
                    wrsp_dict = defaults.VarWrspDict.get()

            # найти и заменить в action.c
            widget.action.SearchAndReplace(
                search=param, wrsp_dict=wrsp_dict, is_param=True, is_wrsp=True, backup=True, wrsp=wrsp)

            w = wrsp_dict['web_reg_num']
            if defaults.VarShowPopupWindow.get() and widget.action.final_wnd_var.get():
                widget.action.search_in_action(word=w)
                s = '{wr}\n\n{wd}'.format(wr=widget.action.web_action.websReport.param_statistic[w], wd=wrsp_dict)
                lr_log.Logger.debug(s)
                tk.messagebox.showinfo(wrsp_dict['param_Name'], s, parent=widget.action)
                try:
                    widget.action.search_res_combo.current(1)
                except tk.TclError:
                    widget.action.search_res_combo.current(0)
                widget.action.tk_text_see()
        elif 'highlight' in mode:
            lr_widj.highlight_mode(widget, param)
            widget.action.tk_text.set_highlight()

@lr_pool.T_POOL_execute_decotator
def rClick_Param(event, *args, **kwargs) -> None:
    '''web_reg_save_param из выделения, меню правой кнопки мыши'''
    widget = event.widget
    try:
        param = widget.selection_get()
        # print('индекс(tk.Text) начала выделения')
        # count = widget.count("1.0", "sel.first")
        # print(count)
        # print('------------------')
    except tk.TclError:
        return lr_log.Logger.warning('сбросилось выделение текста\ntry again', parent=widget)
    try:
        action = widget.action
    except AttributeError:
        action = next(iter(defaults.Window.action_windows))
        action = defaults.Window.action_windows[action]
        widget = action.tk_text

    callback = lambda: mouse_web_reg_save_param(widget, param, *args, set_param=False, **kwargs)
    defaults.Window.get_files(param=param, callback=callback, action=action)


@lr_pool.T_POOL_execute_decotator
def group_param(event, widget=None, params=None, ask=True) -> None:
    '''группа web_reg_save_param из выделения, меню правой кнопки мыши'''
    if widget is None:
        widget = event.widget

    if params is None:
        params = widget.action.group_param_search(widget.selection_get())
    elif params is False:
        params = widget.action.session_params(lb_list=[widget.selection_get()], ask=False)
    if not params:
        return lr_log.Logger.warning('param не найдены! %s' % params, parent=widget.action)

    len_params = len(params)
    lr_log.Logger.info('для создания найдено {} param'.format(len_params))

    if ask:
        y = YesNoCancel(buttons=['Найти', 'Отменить', 'Пропуск'],
                        text_before='найти group param', text_after='%s шт.' % len_params, is_text='\n'.join(params),
                        title='group param', parent=widget.action, default_key='Найти')
        ask = y.ask()
        if ask == 'Найти':
            params = sorted(filter(bool, y.text.split('\n')), key=len, reverse=True)
        elif ask == 'Пропуск':
            params = []
        else:
            return

    unsuccess_params = []  # param обработанные с ошибкой
    wrsp_dict_queue = queue.Queue()

    @lr_pool.T_POOL_execute_decotator
    def thread_wrsp_dict_creator() -> None:
        '''создать wrsp_dicts в потоке, чтобы не терять время, при показе popup окон'''
        for param in params:
            try:
                defaults.VarParam.set(param, action=widget.action, set_file=True)
                wrsp_dict_queue.put_nowait(defaults.VarWrspDict.get())
            except Exception:
                unsuccess_params.append(param)
                lr_log.excepthook(*sys.exc_info())
        wrsp_dict_queue.put_nowait(None)  # stop

    lr_log.Logger.debug('на текущий момент уже создано {} param'.format(
        len(widget.action.web_action.websReport.wrsp_and_param_names)))
    len_params = len(params)
    lr_log.Logger.info('>>> для создания выбрано {} param'.format(len_params))
    proc1 = (len_params / 100) or 1

    def progress(counter: int, param: str, proc1: int, wrsp: str, f=' | fail: %s') -> None:
        '''прогресс'''
        lu = len(unsuccess_params)
        widget.action.toolbar['text'] = 'поиск : {param}\nweb_reg_save_param {counter}/{len_params} : {w} %{u}\n' \
                                        '{wrsp}'.format(
            counter=counter, len_params=len_params, u=(f % lu if lu else ''), w=round(counter / proc1), param=param,
            wrsp=wrsp)
        widget.action.background_color_set(color=None)

    replace_list = []  # [('aFFXt', '{P_9882_4_Window_main_a_FFX_t}'), ('aFFX9', '{P_3768_1_Window_login_a_FFX_9}')]

    widget.action.backup()
    with defaults.Window.block(), widget.action.block():
        defaults.Window._block_ = True
        thread_wrsp_dict_creator()  # создавать wrsp_dicts

        for counter, wrsp_dict in enumerate(iter(wrsp_dict_queue.get, None), start=1):
            wrsp_name = lr_param.param_bounds_setter(wrsp_dict['web_reg_num'])
            wrsp = lr_param.web_reg_save_param.format(**wrsp_dict)
            with contextlib.suppress(Exception):
                widget.action.param_inf_checker(wrsp_dict, wrsp)

            replace_list.append((wrsp_dict['param'], wrsp_name))
            widget.action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)  # вставить web_reg_save_param
            lr_pool.MainThreadUpdater.submit(lambda: progress(counter, wrsp_dict['param'], proc1, wrsp))

        widget.action.web_action.replace_bodys(replace_list)  # заменить
        widget.action.web_action_to_tk_text(websReport=True)  # вставить в action.c
        defaults.Window._block_ = False

    lr_pool.MainThreadUpdater.submit(lambda: final_group_param(
        widget, unsuccess_params=unsuccess_params, log=True))


def final_group_param(widget, unsuccess_params=None, log=False) -> None:
    '''результаты работы group_param'''
    widget.action.set_combo_len()
    widget.action.background_color_set(color='')  # оригинальный цвет

    pl = widget.action.param_counter(all_param_info=False)
    widget.action.toolbar['text'] = pl

    if unsuccess_params:
        err = len(unsuccess_params)
        widget.action.toolbar['text'] = '{s} : {n}\n{pl}'.format(
            s=str(not err).upper(), pl=pl,
            n=('{} param не были созданы ! {}'.format(err, ', '.join(unsuccess_params)) if err else ''))

        lr_log.Logger.error(
            '{} param не были обработаны:\n\t{}\nтребуется пересоздание, с OFF чекбоксом\n'
            '"ограничить max_inf"'.format(err, '\n\t'.join(unsuccess_params)), parent=widget.action)

    if widget.action.final_wnd_var.get():
        repA(widget)
    if log:
        lr_log.Logger.debug(pl)


def repA(widget) -> None:
    '''отчет сокращенный'''
    rep = widget.action.web_action.websReport.all_in_one
    y = YesNoCancel(
        buttons=['OK'], text_before='repA', text_after='self.web_action.websReport.all_in_one',
        is_text=get_json(rep), title='transac_len={}, param_len={}'.format(
            len(rep), len(widget.action.web_action.websReport.wrsp_and_param_names)), parent=widget.action)
    lr_pool.T_POOL_execute_decotator(y.ask)()


def repB(widget, counter=None) -> None:
    '''отчет полный'''
    wr = widget.action.web_action.websReport
    if counter is None:
        counter = len(wr.wrsp_and_param_names)

    obj = [wr.wrsp_and_param_names, wr.rus_webs, wr.google_webs, wr.bad_wrsp_in_usage,
           widget.action.web_action.transactions.sub_transaction, wr.web_transaction_sorted, wr.param_statistic,
           wr.web_snapshot_param_in_count, wr.web_transaction]

    ao = ['wrsp_and_param_names', 'rus_webs', 'google_webs', 'bad_wrsp_in_usage', 'sub_transaction',
          'web_transaction_sorted', 'param_statistic', 'web_snapshot_param_in_count', 'web_transaction']
    tb = ' | '.join('{}:{}'.format(e, a) for e, a in enumerate(ao, start=1))
    st = '\n----\n'
    ta = ('\n\n' + st).join('{}:{}{}{}'.format(e, ao[e - 1], st, get_json(ob)) for e, ob in enumerate(obj, start=1))

    y = YesNoCancel(
        buttons=['OK'], text_before=tb, text_after='{} шт'.format(counter), is_text='\n\n{}'.format(ta),
        title='создано: {} шт.'.format(counter), parent=widget.action)
    lr_pool.T_POOL_execute_decotator(y.ask)()
    lr_log.Logger.trace('{}\n\n{}'.format(tb, ta))


def get_json(obj, indent=10):
    try:
        return json.dumps(obj, indent=indent)
    except Exception:
        return obj


def remove_web_reg_save_param_from_action(event, selection=None) -> None:
    '''удалить web_reg_save_param с w.param или w.name == selection'''
    if selection is None:
        selection = event.widget.selection_get()
    _param = event.widget.action.web_action.web_reg_save_param_remove(selection)
    event.widget.action.web_action_to_tk_text(websReport=True)  # вставить в action.c
    if _param:
        event.widget.action.search_in_action(word=_param)


@lr_pool.T_POOL_execute_decotator
def all_wrsp_dict_web_reg_save_param(event) -> None:
    ''''''
    selection = event.widget.selection_get()
    defaults.VarParam.set(selection, action=event.widget.action, set_file=True)
    defaults.VarWrspDictList.clear()

    wrsp_dict = lr_param.wrsp_dict_creator()
    if wrsp_dict:
        defaults.VarWrspDictList.append([wrsp_dict, lr_param.create_web_reg_save_param(wrsp_dict)])
    else:
        return

    while True:
        try:
            lr_setter.next_3_or_4_if_bad_or_enmpy_lb_rb('поиск всех возможных wrsp_dict')
            wrsp_dict = lr_param.wrsp_dict_creator()
            if wrsp_dict:
                defaults.VarWrspDictList.append([wrsp_dict, lr_param.create_web_reg_save_param(wrsp_dict)])
        except UserWarning:
            break
        except Exception:
            continue

    len_dl = len(defaults.VarWrspDictList)
    y = YesNoCancel(
        buttons=['Заменить текущий', 'Создать новый', 'Выйти'],
        text_before='отображены все найденные варианты, которыми можно создать web_reg_save_param\n'
                    'необходимо оставить только один вариант, удалив остальные.',
        text_after='итого %s вариантов.' % len_dl, is_text='\n\n'.join(w[1] for w in defaults.VarWrspDictList),
        title='{} : {} шт.'.format(selection, len_dl), parent=event.widget.action, default_key='Заменить текущий')
    ask = y.ask()

    if ask == 'Заменить текущий':
        remove_web_reg_save_param_from_action(event, selection=selection)
        ask = 'Создать новый'

    if ask == 'Создать новый':
        user_wrsp = y.text.strip('\n')
        _wrsp = user_wrsp.strip()
        for wrsp_dict, wrsp in defaults.VarWrspDictList:
            if _wrsp == wrsp.strip():
                mouse_web_reg_save_param(event.widget, selection, wrsp=user_wrsp, wrsp_dict=wrsp_dict)
                return


@lr_pool.T_POOL_execute_decotator
def rClick_web_reg_save_param_regenerate(event, new_lb_rb=True) -> None:
    '''из выделения, переформатировать LB/RB в уже созданном web_reg_save_param, меню правой кнопки мыши'''
    selection = event.widget.selection_get()
    try:
        action = event.widget.action
    except:
        action = next(iter(defaults.Window.action_windows.values()))

    if lr_param.wrsp_lr_start not in selection:
        return tk.messagebox.showwarning(
            str(rClick_web_reg_save_param_regenerate),
            'Ошибка, необходимо выделять весь блок, созданного web_reg_save_param, вместе с комментариями\
            nСейчас "{wr}" не содержится в выделенном тексте:\n{selection}'.format(
                wr=lr_param.wrsp_lr_start, selection=selection[:1000]), parent=action)

    file_name = selection.split(lr_param.wrsp_file_start, 1)[-1]
    file_name = file_name.split(lr_param.wrsp_file_end, 1)[0]

    param = selection.split(lr_param.wrsp_start, 1)[-1]
    param = param.split(lr_param.wrsp_end, 1)[0]
    defaults.VarParam.set(param, action=action, set_file=False)  # найти
    defaults.VarFileName.set(file_name)

    sel = selection.split(lr_param.wrsp_lr_start, 1)[-1]
    sel = sel.split(lr_param.wrsp_lr_end, 1)
    wrsp_name, sel = sel[0], sel[-1]

    if new_lb_rb:  # сохранить LB/RB
        wrsp_lb = sel.split(lr_param.wrsp_LB_start, 1)[-1]
        wrsp_lb = wrsp_lb.split(lr_param.wrsp_LB_end, 1)[0]
        wrsp_rb = sel.split(lr_param.wrsp_RB_start, 1)[-1]
        wrsp_rb = wrsp_rb.split(lr_param.wrsp_RB_end, 1)[0]
        defaults.VarLB.set(value=wrsp_lb)
        defaults.VarRB.set(value=wrsp_rb)

    wrsp_dict = lr_param.wrsp_dict_creator()  # сформировать wrsp_dict
    wrsp_dict['web_reg_num'] = wrsp_name  # сохранить старое имя
    web_reg_save_param = lr_param.web_reg_save_param.format(**wrsp_dict)  # создать

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
    defaults.VarSearchMaxInf.set(int(m))


def rClick_min_inf(event) -> None:
    '''min inf widget из выделения, меню правой кнопки мыши'''
    selection = event.widget.selection_get()
    m = re.sub("\D", "", selection)
    defaults.VarSearchMinInf.set(int(m))


def rClick_Search(event) -> None:
    '''поиск выделения в тексте, меню правой кнопки мыши'''
    selection = event.widget.selection_get()
    with contextlib.suppress(AttributeError):
        event.widget.action.search_in_action(word=selection)


def rClick_add_highlight(event, option: str, color: str, val: str, find=False) -> None:
    '''для выделения, добавление color в highlight_dict, меню правой кнопки мыши'''
    try:  # action.c виджет
        highlight = event.widget.highlight_dict
    except AttributeError:
        pass
    else:
        selection = event.widget.selection_get()

        if val == 'добавить':
            if option not in highlight:
                highlight[option] = {color: [selection]}
            elif color not in highlight[option]:
                highlight[option][color] = [selection]
            elif selection not in highlight[option][color]:
                highlight[option][color].add(selection)
        else:
            if option in highlight and color in highlight[option] and selection in highlight[option][color]:
                highlight[option][color].remove(selection)

        event.widget.action.save_action_file(file_name=False)
        if find:
            event.widget.action.search_in_action(word=selection)
            event.widget.action.tk_text_see()


Transac_start = 'lr_start_transaction("'
Transac_end = 'lr_end_transaction("'


@lr_pool.T_POOL_execute_decotator
def rename_transaction(event, parent=None) -> None:
    selection = event.widget.selection_get().strip()
    try:
        old_name = selection.split(Transac_start, 1)[1].split('"', 1)[0]
    except IndexError:
        old_name = selection.split(Transac_end, 1)[1].split('"', 1)[0]

    with contextlib.suppress(AttributeError):
        parent = event.widget.action

    y = YesNoCancel(['Переименовать', 'Отмена'],
                    'Переименовать выделенную(линию) transaction', 'указать только новое имя transaction',
                    'transaction', parent=parent, is_text=old_name)
    s1, s2 = Transac_start+old_name, Transac_end+old_name
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


@lr_pool.T_POOL_execute_decotator
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

    y = YesNoCancel(['заменить', 'Отмена'], 'заменить выделение', 'cp1251', 'cp1251', parent=(action or widget),
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


def rClicker(event) -> str:
    ''' right click context menu for all Tk Entry and Text widgets'''
    with contextlib.suppress(tk.TclError):
        event.widget.focus()
        try: selection = event.widget.selection_get()
        except: selection = None
        rmenu = tk.Menu(None, tearoff=False)

        nclst = [
            ('Копировать', lambda e=event: e.widget.event_generate('<Control-c>')),
            ('Вырезать', lambda e=event: e.widget.event_generate('<Control-x>')),
            ('Вставить', lambda e=event: e.widget.event_generate('<Control-v>')),
            ('* encoding: "РџРµСЂРІ" -> "Перв"', lambda e=event: encoder(e)),
            ('* commit/backup/обновить action.c', lambda e=event: e.widget.action.save_action_file(file_name=False)),
            ('P: wrsp', lambda e=event: all_wrsp_dict_web_reg_save_param(e)),
            ('переименование транзакции', lambda e=event: rename_transaction(e)),
        ]

        if selection:
            nclst.insert(3, ('* поиск выделеного текста', lambda e=event: rClick_Search(e)))
            submenu_param = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label='P: web_reg_save_param', menu=submenu_param, underline=0)

            submenu_param.add_cascade(
                label='* одиночный -> найти и заменить', underline=0,
                command=lambda e=event: rClick_Param(e, mode=['SearchAndReplace']))
            submenu_param.add_cascade(
                label='группа(найти по налалу имени) -> найти и заменить', underline=0,
                command=lambda e=event: group_param(e, params=None))
            submenu_param.add_cascade(
                label='* группа(найти по LB=") -> найти и заменить', underline=0,
                command=lambda e=event: group_param(e, params=False))
            submenu_param.add_cascade(
                label='* готовый -> пересоздать, с измененными LB/RB', underline=0,
                command=lambda e=event: rClick_web_reg_save_param_regenerate(e, new_lb_rb=True))
            submenu_param.add_cascade(
                label='готовый -> пересоздать, с оригинальными LB/RB', underline=0,
                command=lambda e=event: rClick_web_reg_save_param_regenerate(e, new_lb_rb=False))
            submenu_param.add_cascade(
                label='одиночный -> найти и подсветить', underline=0,
                command=lambda e=event: rClick_Param(e, mode=['highlight']))
            submenu_param.add_cascade(
                label='одиночный -> только найти', underline=0,
                command=lambda e=event: rClick_Param(e, mode=[]))
            submenu_param.add_cascade(
                label='* одиночный -> удалить по wrsp или param имени', underline=0,
                command=lambda e=event: remove_web_reg_save_param_from_action(e))

        dt = defaults.VarWrspDict.get()
        web_reg_num = dt.get('web_reg_num')
        param = dt.get('param_Name')

        if web_reg_num or param:
            submenu_goto = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label=' Быстрый перход', menu=submenu_goto, underline=0)

            def action_goto(e: object, _search: str) -> None:
                '''перейти к _search обрасти в action.c'''
                with contextlib.suppress(AttributeError, tk.TclError):
                    event.widget.action.search_entry.set(_search)
                    event.widget.action.search_in_action(event.widget.action.search_entry.get())
                    event.widget.action.tk_text_see()
            if web_reg_num:
                reg_num = '{%s}' % web_reg_num
                cmd = lambda e=event, n=reg_num: action_goto(e, n)
                submenu_goto.add_cascade(label=reg_num, underline=0, command=cmd)
            if param:
                p_wrsp = lr_param.wrsp_start_end.format(param_Name=param)
                submenu_goto.add_cascade(label=p_wrsp, underline=0, command=lambda e=event, n=p_wrsp: action_goto(e, n))

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        if selection:
            submenu_maxmin = tk.Menu(rmenu, tearoff=False)
            submenu_maxmin.add_cascade(label='min', underline=0, command=lambda e=event: rClick_min_inf(e))
            submenu_maxmin.add_cascade(label='max', underline=0, command=lambda e=event: rClick_max_inf(e))
            rmenu.add_cascade(label=' Inf-min/max', menu=submenu_maxmin, underline=0)

            submenu = tk.Menu(rmenu, tearoff=False)
            colors = defaults.VarColorTeg.get()
            submenu.add_cascade(
                label='сорх в файл', underline=0, command=lambda e=event: add_highlight_words_to_file(e))

            for val in ['добавить', 'удалить']:
                vSub = tk.Menu(submenu, tearoff=False)
                submenu.add_cascade(label=val, menu=vSub, underline=0)
                for option in defaults.VarDefaultColorTeg:
                    sub = tk.Menu(vSub, tearoff=False)
                    vSub.add_cascade(label=option, menu=sub, underline=0)
                    for color in colors:
                        sub.add_command(
                            label=color, command=lambda e=event, o=option, c=color, v=val: rClick_add_highlight(
                                e, o, c, v, find=True))

            rmenu.add_cascade(label=' подсветка', menu=submenu, underline=0)

        rmenu.tk_popup(event.x_root + 40, event.y_root + 10, entry="0")
    return "break"


def add_highlight_words_to_file(event) -> None:
    '''сохранить слово для подсветки в файл - "навсегда" '''
    selection = event.widget.selection_get()
    with open(defaults.highlight_words_main_file, 'a') as f:
        f.write(selection + '\n')
    rClick_add_highlight(event, 'foreground', 'olive', 'добавить', find=True)


def rClickbinder(widget, wdg=('Text', 'Entry', 'Listbox', 'Label')) -> None:
    with contextlib.suppress(tk.TclError):
        for b in wdg:
            widget.bind_class(b, sequence='<Button-3>', func=rClicker, add='')


class ToolTip(object):
    '''всплывающие подсказки'''
    toolTips = []
    lock = threading.Lock()

    def __init__(self, widget):
        self.widget = widget
        self.tip = None
        self.x = 0
        self.y = 0

    def showtip(self, text: str) -> None:
        '''Display text in tooltip'''
        if self.toolTips:
            with self.lock:
                for tip in self.toolTips:
                    with contextlib.suppress(Exception):
                        tip.hidetip()
                    with contextlib.suppress(Exception):
                        self.toolTips.remove(tip)
        with self.lock:
            self.toolTips.append(self)
        with contextlib.suppress(Exception):
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            self.tip = tk.Toplevel(self.widget)
            self.tip.wm_overrideredirect(1)
            self.tip.wm_geometry("+%d+%d" % (x, y))
            tk.Label(self.tip, text=text, justify=tk.LEFT, background=defaults.Background, relief=tk.SOLID,
                     borderwidth=1, font=defaults.ToolTipFont).pack(ipadx=0, ipady=0)

    def hidetip(self) -> None:
        with contextlib.suppress(Exception):
            self.tip.destroy()


def widget_values_counter(widget) -> (int, int):
    '''кол-во строк/индекс текущей строки виджета'''
    i = li = 0

    with contextlib.suppress(Exception):
        _i = list(widget['values'])
        i = _i.index(widget.get()) + 1

    with contextlib.suppress(Exception):
        li = len(widget['values'])

    return widget.widgetName, i, li


def createToolTip(widget, text: str) -> None:
    '''всплывающая подсказка для widget'''
    toolTip = ToolTip(widget)

    def enter(event, toolTip=toolTip, text=text, wlines='') -> None:
        wvc = widget_values_counter(widget)
        if any(wvc[1:]):
            wlines = ' * {0} выбрана строка {1} из {2}\n'.format(*wvc)

        toolTip.showtip('{t}{text}'.format(t=wlines, text=text.rstrip()))
        widget.after(int(defaults.VarToolTipTimeout.get()), toolTip.hidetip)  # тк иногда подсказки "зависают"

    def leave(event, toolTip=toolTip) -> None:
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def center_widget(widget) -> None:
    '''center window on screen'''
    widget.withdraw()
    widget.update_idletasks()
    x = (widget.winfo_screenwidth() - widget.winfo_reqwidth()) / 2
    y = (widget.winfo_screenheight() - widget.winfo_reqheight()) / 2
    widget.geometry("+%d+%d" % (x, y))
    widget.deiconify()


class YesNoCancel(tk.Toplevel):
    '''диалог окно, тк велосипед, работает только в потоке'''
    def __init__(self, buttons: [str, ], text_before: str, text_after: str, title: str, parent=None, default_key='',
                 is_text=None, focus=None, combo_dict=None):
        super().__init__(master=parent, padx=0, pady=0)
        self._wind_attributes()
        self.alive_ = True

        self.parent = parent
        self.buttons = {}
        self.queue = queue.Queue()
        self.title(str(title))
        self.default_key = default_key
        self.combo_dict = combo_dict

        self.combo_var = tk.StringVar(value='')
        if self.combo_dict:
            self.combo = ttk.Combobox(self, textvariable=self.combo_var, values=list(self.combo_dict.keys()))

            def enc(*a) -> None:
                callback = self.combo_dict[self.combo_var.get()]
                self.new_text(callback())

            self.combo.bind("<<ComboboxSelected>>", enc)

        self.label1 = tk.Label(self, text=str(text_before), font='Arial 11', padx=0, pady=0)
        self.label1.grid(row=3, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)
        self.label2 = tk.Label(self, text=str(text_after), font='Arial 10', padx=0, pady=0)
        self.label2.grid(row=100, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)

        width = max(map(len, buttons))
        if width > 20: width = 20
        i = 10

        for name in buttons:
            cmd = lambda *a, n=name: self.queue.put_nowait(n)
            self.buttons[name] = tk.Button(
                self, text=name, command=cmd, width=width, font='Arial 9 bold', padx=0, pady=0)
            self.buttons[name].bind("<KeyRelease-Return>", cmd)
            self.buttons[name].grid(row=i, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)
            i += 1

        if self.combo_dict:
            self.combo.grid(row=i + 1, column=0, padx=0, pady=0)

        self.text = ''
        self.tk_text = tk.Text(self, wrap="none", padx=0, pady=0)
        if is_text is not None:
            with contextlib.suppress(Exception):
                height = len(is_text.split('\n'))
                if height > 25:
                    height = 25
                elif height < 5:
                    height = 5
                self.tk_text.configure(height=height)

            self.tk_text.insert(1.0, is_text)
            self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
            self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
            self.tk_text.configure(
                yscrollcommand=self.text_scrolly.set, xscrollcommand=self.text_scrollx.set, padx=0, pady=0)
            self.tk_text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
            self.text_scrollx.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)
            self.text_scrolly.grid(row=0, column=1, sticky=tk.NSEW, padx=0, pady=0)

        if self.buttons:
            if self.default_key not in self.buttons:
                self.default_key = list(self.buttons.keys())[0]
            if not focus:
                self.buttons[self.default_key].focus_set()
            self.buttons[self.default_key].configure(height=2, background='orange')
        if focus:
            focus.focus_set()

    def new_text(self, text: str) -> None:
        '''стереть = новый текст в self.tk_text'''
        self.tk_text.delete(1.0, tk.END)
        self.tk_text.insert(1.0, text)

    def _wind_attributes(self) -> None:
        '''сделать окно похожим на dialog'''
        # self.resizable(width=False, height=False)
        self.attributes('-topmost', True)  # свсегда сверху
        # self.attributes("-toolwindow", 1)  # remove maximize/minimize
        self.protocol('WM_DELETE_WINDOW', self.close)  # remove close_threads
        center_widget(self)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def ask(self) -> str:
        '''приостановить поток, до получения ответа'''
        try:
            return self.queue.get()
        finally:
            self.alive_ = False
            self.text = self.tk_text.get(1.0, tk.END) + '\n'
            self.destroy()
            self.parent.focus_set()

    def close(self) -> None:
        '''отмена при выходе'''
        self.queue.put_nowait(self.default_key)
