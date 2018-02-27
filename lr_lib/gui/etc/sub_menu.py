# -*- coding: UTF-8 -*-
# меню мыши

import contextlib

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.gui.etc.action_lib as lr_action_lib
import lr_lib.gui.etc.group_param as lr_group_param


def rClicker(event) -> str:
    """ right click context menu for all Tk Entry and Text widgets"""
    with contextlib.suppress(tk.TclError):
        event.widget.focus()
        try:
            selection = event.widget.selection_get()
        except:
            selection = None
        rmenu = tk.Menu(None, tearoff=False)

        if selection:
            rmenu.add_cascade(
                label='Web_Reg_Save_Param - все варианты', underline=0,
                command=lambda e=event: lr_action_lib.all_wrsp_dict_web_reg_save_param(e))
            rmenu.add_cascade(
                label='Encoding : "РџРµСЂРІ" -> "Перв"', underline=0,
                command=lambda e=event: lr_action_lib.encoder(e))
            rmenu.add_cascade(
                label='Копировать', underline=0,
                command=lambda e=event: e.widget.event_generate('<Control-c>'))
            rmenu.add_cascade(
                label='Вырезать', underline=0,
                command=lambda e=event: e.widget.event_generate('<Control-x>'))
            rmenu.add_cascade(
                label='Вставить', underline=0,
                command=lambda e=event: e.widget.event_generate('<Control-v>'))
            rmenu.add_cascade(
                label='Поиск выделения в тексте', underline=0,
                command=lambda e=event: lr_action_lib.rClick_Search(e))

            # open
            submenu_open = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label='Открыть как текст', menu=submenu_open, underline=0)

            submenu_open.add_cascade(
                label='файл-ответа (выделить имя файла)', underline=0,
                command=lambda e=event: lr_action_lib.file_from_selection(e))
            submenu_open.add_cascade(
                label='web_.Snapshot (номер из любых цифр выделения)', underline=0,
                command=lambda e=event: lr_action_lib.snapshot_text_from_selection(e))
            submenu_open.add_cascade(
                label='WRSP (выделить имя wrsp/param)', underline=0,
                command=lambda e=event: lr_action_lib.wrsp_text_from_selection(e))

            # param
            submenu_param = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label='web_reg_save_param', menu=submenu_param, underline=0)

            submenu_param.add_cascade(
                label='* одиночный -> найти и заменить', underline=0,
                command=lambda e=event: lr_action_lib.rClick_Param(e, mode=['SearchAndReplace']))

            submenu_param.add_cascade(
                label='группа(найти по налалу имени) -> найти и заменить', underline=0,
                command=lambda e=event: lr_group_param.group_param(e, params=None))

            submenu_param.add_cascade(
                label='* группа(найти по LB=") -> найти и заменить', underline=0,
                command=lambda e=event: lr_group_param.group_param(e, params=False))

            submenu_param.add_cascade(
                label='* готовый -> пересоздать, с измененными LB/RB', underline=0,
                command=lambda e=event: lr_action_lib.rClick_web_reg_save_param_regenerate(e, new_lb_rb=True))

            submenu_param.add_cascade(
                label='готовый -> пересоздать, с оригинальными LB/RB', underline=0,
                command=lambda e=event: lr_action_lib.rClick_web_reg_save_param_regenerate(e, new_lb_rb=False))

            submenu_param.add_cascade(
                label='одиночный -> найти и подсветить', underline=0,
                command=lambda e=event: lr_action_lib.rClick_Param(e, mode=['highlight']))

            submenu_param.add_cascade(
                label='одиночный -> только найти', underline=0,
                command=lambda e=event: lr_action_lib.rClick_Param(e, mode=[]))

            submenu_param.add_cascade(
                label='* одиночный -> удалить по wrsp или param имени', underline=0,
                command=lambda e=event: lr_action_lib.remove_web_reg_save_param_from_action(e))

        nclst = [
            ('Сохр. пользоват. изменения в тексте', lambda e=event: e.widget.action.save_action_file(file_name=False)),
        ]
        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        dt = lr_vars.VarWrspDict.get()
        web_reg_name = dt.get('web_reg_name')
        param = dt.get('param')

        if web_reg_name or param:
            submenu_goto = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label=' Быстрый перход', menu=submenu_goto, underline=0)

            def action_goto(e, _search: str) -> None:
                """перейти к _search обрасти в action.c"""
                with contextlib.suppress(AttributeError, tk.TclError):
                    event.widget.action.search_entry.set(_search)
                    event.widget.action.search_in_action(event.widget.action.search_entry.get())
                    event.widget.action.tk_text_see()

            if web_reg_name:
                n = '{%s}' % web_reg_name
                cmd = lambda e=event, n=n: action_goto(e, n)
                submenu_goto.add_cascade(label=n, underline=0, command=cmd)

            if param:
                p_wrsp = lr_param.wrsp_start_end.format(param=param)
                submenu_goto.add_cascade(label=p_wrsp, underline=0, command=lambda e=event, n=p_wrsp: action_goto(e, n))

        if selection:
            # other
            submenu_other = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label='Разное', menu=submenu_other, underline=0)
            submenu_other.add_cascade(
                label='Переименовать транзакцию (выделить линию целиком)', underline=0,
                command=lambda e=event: lr_action_lib.rename_transaction(e))
            submenu_other.add_cascade(
                label='Файлы-ответов Snapshot (выделить номер)', underline=0,
                command=lambda e=event: lr_action_lib.snapshot_files(e.widget))

            # maxmin
            submenu_maxmin = tk.Menu(submenu_other, tearoff=False)
            submenu_maxmin.add_cascade(label='min', underline=0, command=lambda e=event: lr_action_lib.rClick_min_inf(e))
            submenu_maxmin.add_cascade(label='max', underline=0, command=lambda e=event: lr_action_lib.rClick_max_inf(e))
            submenu_other.add_cascade(label=' Snapshot-min/max (номер из любых цифр выделения)', menu=submenu_maxmin, underline=0)

            submenu = tk.Menu(submenu_other, tearoff=False)
            colors = lr_vars.VarColorTeg.get()
            submenu.add_cascade(label='сорх в файл', underline=0, command=lambda e=event: lr_action_lib.add_highlight_words_to_file(e))

            for val in ['добавить', 'удалить']:
                vSub = tk.Menu(submenu, tearoff=False)
                submenu.add_cascade(label=val, menu=vSub, underline=0)
                for option in lr_vars.VarDefaultColorTeg:
                    sub = tk.Menu(vSub, tearoff=False)
                    vSub.add_cascade(label=option, menu=sub, underline=0)
                    for color in colors:
                        def cmd(e=event, o=option, c=color, v=val, f=True):
                            return lr_action_lib.rClick_add_highlight(e, o, c, v, find=f)
                        sub.add_command(label=color, command=cmd)

            submenu_other.add_cascade(label=' подсветка', menu=submenu, underline=0)

        rmenu.tk_popup(event.x_root + 40, event.y_root + 10, entry="0")
    return "break"


def rClickbinder(widget, wdg=('Text', 'Entry', 'Listbox', 'Label')) -> None:
    with contextlib.suppress(tk.TclError):
        for b in wdg:
            widget.bind_class(b, sequence='<Button-3>', func=rClicker, add='')
