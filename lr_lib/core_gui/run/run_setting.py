# -*- coding: UTF-8 -*-
# окно Настраиваемый запуск поиска WRSP

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import os
from typing import List

import lr_lib
import lr_lib.core.etc.lbrb_from_disk
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_param
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_lb
import lr_lib.core_gui.group_param.gp_act_re
import lr_lib.core_gui.group_param.gp_act_resp_split
import lr_lib.core_gui.group_param.gp_act_start
import lr_lib.core_gui.group_param.gp_lb_post
import lr_lib.core_gui.group_param.gp_response_re
import lr_lib.core_gui.rename
import lr_lib.gui.widj.dialog
import lr_lib.gui.widj.tooltip
from lr_lib.core.var.etc.vars_other import T_POOL_decorator
from lr_lib.core_gui.group_param.gp_filter import param_sort
from lr_lib.core_gui.run.r_item import RItem
from lr_lib.core_gui.run.r_other import block
from lr_lib.core_gui.run.r_texts import TT_N, TT_PN, TT_MinP, TT_LB, TT_SPL, TT_RE, TT_REP, TT_LBP
from lr_lib.gui.etc.color_progress import progress_decor
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP


class RunSettingWindow(tk.Toplevel):
    """
    Настраиваемый запуск поиска WRSP
    """

    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow'):
        super().__init__(padx=0, pady=0)
        self.action = parent
        self.transient(self.action)
        self.resizable(width=False, height=False)
        a = 'Поиск {param} различными способами, с выбором места поиска, и создание WRSP'
        self.title(a)
        self._is_block_ = False

        # LabelFrame
        self.main_label = tk.LabelFrame(
            self, text='', bd=0,
        )

        # LabelFrame
        self.tool_label = tk.LabelFrame(
            self.main_label, text='дополнительные настройки:', bd=1,
        )

        #
        self.item1 = RItem(
            self, lr_lib.core_gui.group_param.gp_act_lb.group_param_search_by_lb,
            '1) по LB',
            label_title=TT_LB,
            _act_num=0,
            files_req=True,
            files_resp=True,
            files_other=True,
            only_in_act_param=True,
            enable=True,
        )
        self.item2 = RItem(
            self, lr_lib.core_gui.group_param.gp_act_re.group_param_search_by_act_re,
            '2) по regexp',
            label_title=TT_RE,
            _act_num=0,
            files_req=True,
            files_resp=True,
            files_other=False,
            only_in_act_param=True,
            enable=False,
        )
        self.item3 = RItem(
            self, lr_lib.core_gui.group_param.gp_response_re.group_param_search_by_resp_re,
            '3) по regexp c постобработкой результата',
            label_title=TT_REP,
            _act_num=0,
            files_req=False,
            files_resp=True,
            files_other=True,
            only_in_act_param=True,
            enable=True,
        )
        self.item4 = RItem(
            self, lr_lib.core_gui.group_param.gp_act_resp_split.group_param_search_by_split,
            '4) split способ',
            label_title=TT_SPL,
            _act_num=0,
            files_req=True,
            files_resp=True,
            files_other=True,
            only_in_act_param=True,
            enable=False,
        )
        self.item_last_startsw = RItem(
            self, lr_lib.core_gui.group_param.gp_act_start.group_param_search_by_exist_param,
            '5) LAST: по начальным символам известных',
            label_title=TT_N,
            _act_num=0,
            files_req=True,
            files_resp=True,
            files_other=True,
            only_in_act_param=True,
            enable=True,
        )
        self.item_last_lb = RItem(
            self, lr_lib.core_gui.group_param.gp_lb_post.group_param_search_by_lb_post,
            '6) LAST: по LB известных',
            label_title=TT_LBP,
            _act_num=0,
            files_req=True,
            files_resp=True,
            files_other=True,
            only_in_act_param=True,
            enable=False,
        )

        # LabelFrame
        ttt = 'Дополнительные правила поиска {param} для методов 1), 5), 6)'
        self.disk_search_label = tk.LabelFrame(
            self.main_label, text=ttt, font='Arial 7 bold',
        )

        # Checkbutton
        self.disk_wr_part = tk.Checkbutton(
            self.disk_search_label, anchor=tk.E, text='disk_wr', font=lr_vars.DefaultFont,
            variable=lr_lib.core.var.vars_param.disk_wr_part_var,
        )
        yy1 = 'Добавить дополнительные варианты поиска, для метода 5)\n' \
              'Из файла {f}\nЭто файл уже готовых скриптов на диске,\n' \
              'его необходимо периодически/в первый раз сформировать кнопкой "поиск новых правил lb/param"'.format(
            f=lr_lib.core.var.vars_param.WFILE)
        lr_lib.gui.widj.tooltip.createToolTip(self.disk_wr_part, yy1)

        # Checkbutton
        self.disk_lb = tk.Checkbutton(
            self.disk_search_label, anchor=tk.E, text='disk_lb', font=lr_vars.DefaultFont,
            variable=lr_lib.core.var.vars_param.disk_lb_var,
        )
        yy2 = 'Добавить дополнительные варианты поиска, для методов 1), 6)\n' \
              'Из файла {f}\nЭто файл уже готовых скриптов на диске,\n' \
              'его необходимо периодически/в первый раз сформировать кнопкой "поиск новых правил lb/param"'.format(
            f=lr_lib.core.var.vars_param.LFILE)
        lr_lib.gui.widj.tooltip.createToolTip(self.disk_lb, yy2)

        # Button
        def disk_run_start():
            d = tk.filedialog.askdirectory()
            if d:
                (wr_n, lb_n) = lr_lib.core.etc.lbrb_from_disk.main(d)
                t = self.disk_search_label['text'].rsplit(':', 1)[0]
                t = '{0}: Найдено новых param={1}, LB={2}'.format(t, wr_n, lb_n)
                self.disk_search_label['text'] = t
                self.disk_search_label.update()
            return
        tt_tr = 'поиск новых правил lb/param из любых *.c скриптов выбранного каталога'
        self.disk_run = tk.Button(
            self.disk_search_label, font='Arial 8 bold', text=tt_tr, relief='groove', command=disk_run_start,
            bg='Orange',
        )
        se = '\nВыбрать директорию из диалог окна\n' \
             'Поиск произойдет во всех *.с файлах/под-директориях выбранной директории\n' \
             'Результаты поиска сохрянятся в файлы, в каталог утилиты,\n' \
             'и могут быть использованы в дальнейшем, для поиска wrsp'
        lr_lib.gui.widj.tooltip.createToolTip(self.disk_run, (tt_tr + se))

        # Button
        tt_tr = 'Запуск'
        self.btn_run = tk.Button(
            self.main_label, font='Arial 8 bold', text=tt_tr, bd=10, relief='groove', command=self.run, bg='Orange',
        )

        # Spinbox
        self.secondary_param_spin = tk.Spinbox(
            self.tool_label, width=2, justify='center', from_=0, to=99,
            textvariable=lr_vars.SecondaryParamLen,
        )
        lr_lib.gui.widj.tooltip.createToolTip(self.secondary_param_spin, TT_PN)

        # Spinbox
        def _MinParamLen_minus_1(*args) -> None:
            """тк нумерация с 0"""
            n = lr_vars._MinParamLen.get()
            lr_vars.MinParamLen = n
            return

        self.min_param_spin = tk.Spinbox(
            self.tool_label, width=2, justify='center', from_=0, to=99, bg='orange',
            textvariable=lr_vars._MinParamLen, command=_MinParamLen_minus_1,
        )
        rr2 = 'Минимальная длина любого {param}.\nОтфильтровывать {param} с меньшей длиной.'
        lr_lib.gui.widj.tooltip.createToolTip(self.min_param_spin, rr2)

        # Spinbox
        self.min_num_param_spin = tk.Spinbox(
            self.tool_label, width=2, justify='center', from_=0, to=99,
            textvariable=lr_vars.MinParamNumsOnlyLen,
        )
        lr_lib.gui.widj.tooltip.createToolTip(self.min_num_param_spin, TT_MinP)

        # Checkbutton
        def cmd1() -> None:
            """VarFirstLastFile и DefaultActionAddSnapshot должны быть противоположными"""
            s = (not lr_vars.VarFirstLastFile.get())
            lr_vars.DefaultActionAddSnapshot.set(s)
            return
        self.cbxFirstLastFile = tk.Checkbutton(
            self.tool_label, variable=lr_vars.VarFirstLastFile, text='reverse', font=lr_vars.DefaultFont,
            padx=0, pady=0, command=cmd1, bg='orange',
        )
        lr_lib.gui.widj.tooltip.createToolTip(self.cbxFirstLastFile, lr_vars.Window._T2)

        # Checkbutton
        self.add_inf_cbx = tk.Checkbutton(
            self.tool_label, anchor=tk.E, text='max inf', font=lr_vars.DefaultFont,
            variable=lr_vars.DefaultActionAddSnapshot, bg='orange',
        )
        lr_lib.gui.widj.tooltip.createToolTip(self.add_inf_cbx, self.action._T1)

        # Checkbutton
        self.only_numeric = tk.Checkbutton(
            self.tool_label, anchor=tk.E, text='num', font=lr_vars.DefaultFont,
            variable=lr_vars.AllowOnlyNumericParam,
        )
        tt20 = 'Разрешить имена {param}, состоящие только из цифр\n например: 11235432\n\n' \
               'Запретить, если какие-либо методы поиска {param}, находят порты 18080 и подобное.\n' \
               'Либо ограничичь, минимильную длину param из цифр, спинбоксом.'
        lr_lib.gui.widj.tooltip.createToolTip(self.only_numeric, tt20)

        # Checkbutton
        self.deny_enable = tk.Checkbutton(
            self.tool_label, anchor=tk.E, text='deny', font=lr_vars.DefaultFont,
            variable=lr_lib.core.var.vars_param.DENY_ENABLE,
        )
        tt21 = 'Отфильтровывать имена {param} из списка запрешенных имен.\nТеоритически может отфильтровать нужное.'
        lr_lib.gui.widj.tooltip.createToolTip(self.deny_enable, tt21)

        # Checkbutton
        self.multiWRSP = tk.Checkbutton(
            self.tool_label, anchor=tk.E, text='multiWRSP', font=lr_vars.DefaultFont,
            variable=lr_lib.core.var.vars.WRSPCreateMultiParamMode,
        )
        tt21 = 'ON - Найти и создать web_reg_save_param, в аспекте того, что он может обновиться/переопределиться ' \
               'по мере выполнения теста.\n' \
               'Если {param}, используется в нескольких web, ' \
               'и его можно создать используя несколько разных web, \nто попытатся создать отдельный wrsp, ' \
               'для неодинаковых wrsp, для param из разных web.\n' \
               'OFF - по старому, один web_reg_save_param на каждый param.'
        lr_lib.gui.widj.tooltip.createToolTip(self.multiWRSP, tt21)

        # grid
        self.main_label.grid(row=0, column=0)

        self.item1.main_label.grid(row=1, column=1, sticky=tk.W, columnspan=3)
        self.item2.main_label.grid(row=2, column=1, sticky=tk.W, columnspan=3)
        self.item3.main_label.grid(row=3, column=1, sticky=tk.W, columnspan=3)
        self.item4.main_label.grid(row=1, column=4, sticky=tk.W, columnspan=3)
        self.item_last_startsw.main_label.grid(row=2, column=4, sticky=tk.W, columnspan=3)
        self.item_last_lb.main_label.grid(row=3, column=4, sticky=tk.W, columnspan=3)

        self.disk_search_label.grid(row=50, column=0, sticky=tk.NSEW, rowspan=10, columnspan=50, )
        self.disk_wr_part.grid(row=1, column=1, sticky=tk.NSEW, )
        self.disk_lb.grid(row=1, column=2, sticky=tk.NSEW, )
        self.disk_run.grid(row=1, column=3, sticky=tk.NSEW, )

        self.btn_run.grid(row=0, column=4, sticky=tk.NSEW, rowspan=1, columnspan=10, )
        self.tool_label.grid(row=0, column=0, sticky=tk.NSEW, rowspan=1, columnspan=4, )

        self.secondary_param_spin.grid(row=5, column=2, sticky=tk.NSEW, rowspan=10, columnspan=1)
        self.min_param_spin.grid(row=5, column=7, sticky=tk.NSEW, rowspan=10, columnspan=1)

        self.min_num_param_spin.grid(row=5, column=6, sticky=tk.NSEW, rowspan=10, columnspan=1)
        self.only_numeric.grid(row=5, column=5, sticky=tk.NSEW, rowspan=10, columnspan=1)
        self.deny_enable.grid(row=5, column=8, sticky=tk.NSEW, rowspan=10, columnspan=1)

        self.multiWRSP.grid(row=30, column=0, sticky=tk.NSEW, columnspan=10)

        self.cbxFirstLastFile.grid(row=5, column=3, sticky=tk.NSEW, rowspan=10, columnspan=1)
        self.add_inf_cbx.grid(row=5, column=4, sticky=tk.NSEW, rowspan=10, columnspan=1)

        #
        lr_lib.gui.etc.gui_other.center_widget(self)
        #
        self.items = [
            self.item1,
            self.item2,
            self.item3,
            self.item4,
        ]
        self.last_items = [
            self.item_last_startsw,
            self.item_last_lb,
        ]
        #
        self.block_items = [
            self, self.main_label,
            self.item1, self.item2, self.item3, self.item4,
            self.item_last_startsw, self.item_last_lb,
        ]
        return

    @T_POOL_decorator
    def run(self) -> None:
        """
        запуск
        """
        if not tkinter.messagebox.askokcancel('Продолжить?', 'создание WRSP', parent=self):
            return

        with block(self):
            self._run()
        return

    def _run(self) -> None:
        """
        запуск
        """
        params = set()

        def param_count_search_info(item: 'RItem', i_params: List[str]) -> None:
            """сколько param, нашел конкретный метод поиска"""
            if not isinstance(i_params, set):
                i_params = set(i_params)
            add = len(i_params)
            new = len(i_params - params)
            item.search_label_text(add, new)
            return

        #  --> поиск param -->
        for item in self.items:
            i_params = item.get_params()
            param_count_search_info(item, i_params)
            params.update(i_params)
            continue
        params = set(param_sort(params, deny_param_filter=True))  # фильтровать

        # LAST1
        item = self.last_items[0]
        i_params = item.get_params(i_params=params)
        param_count_search_info(item, i_params)
        params.update(i_params)
        params = set(param_sort(params, deny_param_filter=True))  # фильтровать

        # LAST2
        item = self.last_items[1]
        i_params = item.get_params(i_params=params)
        param_count_search_info(item, i_params)
        params.update(i_params)
        if lr_lib.core.var.vars_param.disk_lb_var.get():
            f = os.path.join(lr_vars.lib_folder, lr_lib.core.var.vars_param.LFILE)
            if os.path.exists(f):
                with open(f, errors='replace') as f:
                    for _lb in filter(str.strip, f):
                        params.add(_lb)
                        continue
        params = param_sort(params, deny_param_filter=True)  # фильтровать
        #  <-- поиск param <--

        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[K_FIND, K_SKIP],
            default_key=K_FIND,
            title='создание WRSP',
            is_text='\n'.join(params),
            text_before='итого {} шт.'.format(len(params)),
            text_after='добавить/удалить: необходимо удалить "лишнее", то что не является param',
            parent=self.action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()

        # создание param
        if ans == K_FIND:
            params = y.text.split('\n')
            params = param_sort(params, deny_param_filter=False)
            self.after(500, self.destroy)
            lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=self.action.tk_text, ask=False)
        else:
            return
        return
