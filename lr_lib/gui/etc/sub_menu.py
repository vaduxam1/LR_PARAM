﻿# -*- coding: UTF-8 -*-
# меню мыши

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.etc.vars_other
import lr_lib.core_gui.action_lib
import lr_lib.core_gui.all_wrsp
import lr_lib.core_gui.group_param.gp_act_lb
import lr_lib.core_gui.group_param.gp_act_start
import lr_lib.core_gui.rename
import lr_lib.gui.etc.color_progress
from lr_lib.gui.etc.color_progress import progress_decor


def rClicker(event) -> str:
    """
    right click context menu for all Tk Entry and Text widgets
    """
    try:
        event.widget.focus()
        action = lr_lib.core_gui.action_lib.event_action_getter(event)

        try:
            selection = event.widget.selection_get()
        except:
            selection = None
        rmenu = tk.Menu(None, tearoff=False)

        if selection:
            cmd1 = lambda e=event: lr_lib.core_gui.all_wrsp.all_wrsp_dict_web_reg_save_param(e)
            rmenu.add_cascade(label='Web_Reg_Save_Param - все варианты', underline=0, command=cmd1,)

            cmd2 = lambda e=event: lr_lib.core_gui.action_lib.encoder(e)
            rmenu.add_cascade(label='Encoding : "РџРµСЂРІ" -> "Перв"', underline=0, command=cmd2,)

            cmd3 = lambda e=event: e.widget.event_generate('<Control-c>')
            rmenu.add_cascade(label='Копировать', underline=0, command=cmd3,)

            cmd4 = lambda e=event: e.widget.event_generate('<Control-x>')
            rmenu.add_cascade(label='Вырезать', underline=0, command=cmd4,)

            cmd5 = lambda e=event: e.widget.event_generate('<Control-v>')
            rmenu.add_cascade(label='Вставить', underline=0, command=cmd5,)

            cmd6 = lambda e=event: lr_lib.core_gui.action_lib.rClick_Search(e)
            rmenu.add_cascade(label='Поиск выделения в тексте', underline=0, command=cmd6,)

            # open
            submenu_open = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label='Открыть как текст', menu=submenu_open, underline=0)

            cmd7 = lambda e=event: lr_lib.core_gui.action_lib.file_from_selection(e)
            submenu_open.add_cascade(label='файл-ответа (выделить имя файла)', underline=0, command=cmd7,)

            cmd8 = lambda e=event: lr_lib.core_gui.action_lib.snapshot_text_from_selection(e)
            submenu_open.add_cascade(label='web_.Snapshot (номер из любых цифр выделения)', underline=0, command=cmd8,)

            cmd9 = lambda e=event: lr_lib.core_gui.action_lib.wrsp_text_from_selection(e)
            submenu_open.add_cascade(label='WRSP (выделить имя wrsp/param)', underline=0, command=cmd9,)

            # param
            submenu_param = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label='web_reg_save_param', menu=submenu_param, underline=0)

            def cmd10(e=event) -> None:
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                fn = progress_decor(lr_lib.core_gui.action_lib.rClick_Param, action)
                fn(e, mode=['SearchAndReplace', ])
                return
            submenu_param.add_cascade(label='* одиночный -> найти и заменить', underline=0, command=cmd10,)

            @lr_lib.core.var.etc.vars_other.T_POOL_decorator
            def cmd11(e=event) -> None:
                b = e.widget.selection_get()
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                w = [['web', action], 'all']
                fn = progress_decor(lr_lib.core_gui.group_param.gp_act_start.group_param_search_by_name, action)
                fn(action, w, wrsp_create=True, text=b)
                return
            submenu_param.add_cascade(label='группа(по налалу имени) -> найти и заменить', underline=0, command=cmd11,)

            @lr_lib.core.var.etc.vars_other.T_POOL_decorator
            def cmd12(e=event) -> None:
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                w = [['web', action], 'all']
                b = [e.widget.selection_get(), ]
                fn = progress_decor(lr_lib.core_gui.group_param.gp_act_lb.group_param_search_by_lb, action)
                fn(action, w, wrsp_create=True, lb_items=b, ask=False, MutableLBRegs=(),)
                return
            submenu_param.add_cascade(label='* группа(по LB=") -> найти и заменить', underline=0, command=cmd12,)

            def cmd13(e=event) -> None:
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                fn = progress_decor(lr_lib.core_gui.action_lib.rClick_web_reg_save_param_regenerate, action)
                fn(e, new_lb_rb=True,)
                return
            submenu_param.add_cascade(label='* готовый -> пересоздать, с измененными LB/RB', underline=0,command=cmd13,)

            def cmd14(e=event) -> None:
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                fn = progress_decor(lr_lib.core_gui.action_lib.rClick_web_reg_save_param_regenerate, action)
                fn(e, new_lb_rb=False,)
                return
            submenu_param.add_cascade(label='готовый -> пересоздать, с оригинальными LB/RB', underline=0,command=cmd14,)

            def cmd15(e=event) -> None:
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                fn = progress_decor(lr_lib.core_gui.action_lib.rClick_Param, action)
                fn(e, mode=['highlight'],)
                return
            submenu_param.add_cascade(label='одиночный -> найти и подсветить', underline=0, command=cmd15,)

            def cmd16(e=event) -> None:
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                fn = progress_decor(lr_lib.core_gui.action_lib.rClick_Param, action)
                fn(e, mode=[],)
                return
            submenu_param.add_cascade(label='одиночный -> только найти', underline=0, command=cmd16,)

            def cmd17(e=event) -> None:
                action = lr_lib.core_gui.action_lib.event_action_getter(e)
                fn = progress_decor(lr_lib.core_gui.action_lib.remove_web_reg_save_param_from_action, action)
                fn(e)
                return
            submenu_param.add_cascade(label='* одиночный -> удалить по wrsp или param', underline=0, command=cmd17,)

        cmd_18 = lambda e=event: lr_lib.core_gui.action_lib.event_action_getter(e).save_action_file(file_name=False)
        # cmd_19 = lambda e=event: lr_lib.core_gui.action_lib.event_action_getter(e).save_action_file_many(file_name=False)

        nclst = [
            ('Сохр. пользоват. изменения в тексте, в один файл', cmd_18),
            # ('Сохр. пользоват. изменения в тексте, в vuser_init.c/action.c/.../vuser_end.c файлы', cmd_19),
        ]
        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)
            continue

        dt = lr_vars.VarWrspDict.get()
        web_reg_name = dt.get('web_reg_name')
        param = dt.get('param')

        # goto
        submenu_goto = tk.Menu(rmenu, tearoff=False)
        rmenu.add_cascade(label='Переход по тексту', menu=submenu_goto, underline=0)
        ntn = action.web_action.transactions._no_transaction_name
        tss_filter = lambda vals: [v for v in vals if (ntn not in v)]
        snaps = action.web_action.get_web_snapshot_all()

        z_values = zip(
            [
                'transaction start',
                'transaction end',
                'web_reg_save_param',
                'param',
                'все Snapshot',
                'с русскими буквами',
                'Snapshot с WARNING',
            ],  # name
            [
                tss_filter(action.web_action.transactions.start_stop['start']),
                tss_filter(action.web_action.transactions.start_stop['stop']),
                action.web_action.websReport.wrsp_and_param_names.keys(),
                action.web_action.websReport.wrsp_and_param_names.values(),
                action.web_action.action_infs,
                action.web_action.websReport.rus_webs.keys(),
                [str(w.snapshot.inf) for w in snaps if w.warning],
            ],  # value
            [
                'lr_start_transaction("',
                'lr_end_transaction("',
                '"',
                '"',
                '"Snapshot=t',
                '"Snapshot=t',
                '"Snapshot=t',
            ],  # add_start
            [
                '"',
                '"',
                '"',
                '"',
                '.inf",',
                '.inf",',
                '.inf",',
            ],  # add_end
        )
        for (name, values, add_start, add_end) in z_values:
            vSub = tk.Menu(submenu_goto, tearoff=False)
            submenu_goto.add_cascade(label=name, menu=vSub, underline=0)

            for value in values:
                def _cmd(event=event, value=value, add_start=add_start, add_end=add_end) -> None:
                    """перейти по тексту в action.c"""
                    search = '{0}{1}{2}'.format(add_start, value, add_end)
                    action_goto(event, search)
                    return

                vSub.add_command(label=value, command=_cmd)
                continue
            continue

        if web_reg_name or param:
            submenu_goto = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label=' Быстрый перход', menu=submenu_goto, underline=0)

            if web_reg_name:
                n = ('{%s}' % web_reg_name)
                cmd = lambda e=event, n=n: action_goto(e, n)
                submenu_goto.add_cascade(label=n, underline=0, command=cmd)

            if param:
                p_wrsp = lr_lib.core.wrsp.param.wrsp_start_end.format(param=param)
                cmd19 = lambda e=event, n=p_wrsp: action_goto(e, n)
                submenu_goto.add_cascade(label=p_wrsp, underline=0, command=cmd19)

        if selection:
            # other
            submenu_other = tk.Menu(rmenu, tearoff=False)
            rmenu.add_cascade(label='Разное', menu=submenu_other, underline=0)

            cmd20 = lambda e=event: lr_lib.core_gui.rename.rename_transaction(e)
            submenu_other.add_cascade(label='Переименовать транзакцию (выделить линию)', underline=0, command=cmd20,)

            cmd21 = lambda e=event: lr_lib.core_gui.action_lib.snapshot_files(e.widget)
            submenu_other.add_cascade(label='Файлы-ответов Snapshot (выделить номер)', underline=0, command=cmd21,)

            # maxmin
            submenu_maxmin = tk.Menu(submenu_other, tearoff=False)

            cmd22 = lambda e=event: lr_lib.core_gui.action_lib.rClick_min_inf(e)
            submenu_maxmin.add_cascade(label='min', underline=0, command=cmd22,)

            cmd23 = lambda e=event: lr_lib.core_gui.action_lib.rClick_max_inf(e)
            submenu_maxmin.add_cascade(label='max', underline=0, command=cmd23,)

            submenu_other.add_cascade(label=' Snapshot-min/max', menu=submenu_maxmin, underline=0,)

            submenu = tk.Menu(submenu_other, tearoff=False)
            colors = lr_lib.core.var.vars_highlight.VarColorTeg.get()

            cmd24 = lambda e=event: lr_lib.core_gui.action_lib.add_highlight_words_to_file(e)
            submenu.add_cascade(label='сорх в файл', underline=0, command=cmd24,)

            vald = 'удалить'

            def cmd26(e=event, o='', c='', v=vald, f=True) -> None:
                """remove_highlight"""
                lr_lib.core_gui.action_lib.rClick_add_highlight(e, o, c, v, find=f)
                return

            submenu.add_cascade(label=vald, underline=0, command=cmd26, )

            # подсветка
            val = 'добавить'
            vSub = tk.Menu(submenu, tearoff=False)
            submenu.add_cascade(label=val, menu=vSub, underline=0)
            for option in lr_lib.core.var.vars_highlight.VarDefaultColorTeg:
                sub = tk.Menu(vSub, tearoff=False)
                vSub.add_cascade(label=option, menu=sub, underline=0)
                for color in colors:

                    def _cmd(e=event, o=option, c=color, v=val, f=True) -> None:
                        """add_highlight"""
                        lr_lib.core_gui.action_lib.rClick_add_highlight(e, o, c, v, find=f)
                        return

                    sub.add_command(label=color, command=_cmd)
                    continue
                continue

            submenu_other.add_cascade(label=' подсветка', menu=submenu, underline=0)

        rmenu.tk_popup((event.x_root + 40), (event.y_root + 10), entry="0")

    except tk.TclError as ex:
        pass
    return "break"


def action_goto(event, _search: str) -> None:
    """
    перейти к _search обрасти в action.c
    """
    action = lr_lib.core_gui.action_lib.event_action_getter(event)
    try:
        action.search_entry.set(_search)
        ev = action.search_entry.get()
        action.search_in_action(ev)
        action.tk_text_see()
    except (AttributeError, tk.TclError) as ex:
        pass
    return


def rClickbinder(widget, wdg=('Text', 'Entry', 'Listbox', 'Label')) -> None:
    """
    добавить на виджет, меню правой кнопки мыши
    """
    for b in wdg:  #
        try:
            widget.bind_class(b, sequence='<Button-3>', func=rClicker, add='')
        except tk.TclError as ex:
            pass
        continue
    return
