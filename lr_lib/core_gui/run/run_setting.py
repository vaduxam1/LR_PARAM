# -*- coding: UTF-8 -*-
# окно Настраиваемый запуск поиска WRSP

import tkinter as tk
import tkinter.messagebox

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_lb
import lr_lib.core_gui.group_param.gp_act_re
import lr_lib.core_gui.group_param.gp_act_start
import lr_lib.core_gui.group_param.gp_filter
import lr_lib.core_gui.group_param.gp_response_re
import lr_lib.core_gui.group_param.gp_act_resp_split
import lr_lib.core_gui.group_param.gp_lb_post
import lr_lib.core_gui.rename
import lr_lib.gui.widj.dialog
import lr_lib.gui.widj.tooltip
from lr_lib.core.var.vars_other import T_POOL_decorator
from lr_lib.core_gui.run.r_item import RItem
from lr_lib.core_gui.run.r_other import block
from lr_lib.core_gui.run.r_texts import TT_N, TT_PN, TT_MinP, TT_LB, TT_SPL, TT_RE, TT_REP, TT_LBP
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP
from lr_lib.gui.etc.color_progress import progress_decor


class RunSettingWindow(tk.Toplevel):
    """Настраиваемый запуск поиска WRSP"""
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
        )

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
        def _MinParamLen_minus_1(*args):
            """тк нумерация с 0"""
            n = lr_vars._MinParamLen.get()
            lr_vars.MinParamLen = (n - 1)
            return

        self.min_param_spin = tk.Spinbox(
            self.tool_label, width=2, justify='center', from_=0, to=99,
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
        self.cbxFirstLastFile = tk.Checkbutton(
            self.tool_label, variable=lr_vars.VarFirstLastFile, text='reverse', font=lr_vars.DefaultFont + ' italic',
            padx=0, pady=0,
        )
        lr_lib.gui.widj.tooltip.createToolTip(self.cbxFirstLastFile, lr_vars.Window._T2)

        # Checkbutton
        self.add_inf_cbx = tk.Checkbutton(
            self.tool_label, anchor=tk.E, text='max inf mode', font=lr_vars.DefaultFont,
            variable=lr_vars.DefaultActionAddSnapshot,
        )
        lr_lib.gui.widj.tooltip.createToolTip(self.add_inf_cbx, self.action._T1)

        # grid
        self.main_label.grid(row=0, column=0)

        self.item1.main_label.grid(row=1, column=1, sticky=tk.W, columnspan=3)
        self.item2.main_label.grid(row=2, column=1, sticky=tk.W, columnspan=3)
        self.item3.main_label.grid(row=3, column=1, sticky=tk.W, columnspan=3)
        self.item4.main_label.grid(row=1, column=4, sticky=tk.W, columnspan=3)
        self.item_last_startsw.main_label.grid(row=2, column=4, sticky=tk.W, columnspan=3)
        self.item_last_lb.main_label.grid(row=3, column=4, sticky=tk.W, columnspan=3)

        self.btn_run.grid(row=0, column=4, sticky=tk.NSEW, rowspan=1, columnspan=10, )
        self.tool_label.grid(row=0, column=0, sticky=tk.NSEW, rowspan=1, columnspan=4, )

        self.secondary_param_spin.grid(row=5, column=4, sticky=tk.NSEW, rowspan=10, columnspan=1)
        self.min_param_spin.grid(row=5, column=5, sticky=tk.NSEW, rowspan=10, columnspan=1)
        self.min_num_param_spin.grid(row=5, column=6, sticky=tk.NSEW, rowspan=10, columnspan=1)

        self.cbxFirstLastFile.grid(row=5, column=3, sticky=tk.NSEW, rowspan=10, columnspan=1)
        self.add_inf_cbx.grid(row=5, column=2, sticky=tk.NSEW, rowspan=10, columnspan=1)

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
        """запуск"""
        if not tkinter.messagebox.askokcancel('Продолжить?', 'создание WRSP', parent=self):
            return

        with block(self):
            self._run()
        return

    def _run(self) -> None:
        """запуск"""
        params = set()
        for item in self.items:
            i_params = item.get_params()
            params.update(i_params)
            continue

        sp = set(params)
        self.item_last_startsw.kwargs['exist_params'] = sp
        item = self.last_items[0]
        i_params = item.get_params()
        params.update(i_params)

        self.item_last_startsw.kwargs['exist_params'] = params
        item = self.last_items[1]
        i_params = item.get_params()
        params.update(i_params)

        y = lr_lib.gui.widj.dialog.YesNoCancel(
            [K_FIND, K_SKIP],
            default_key=K_FIND,
            title='создание WRSP',
            is_text='\n'.join(params),
            text_before='итого {} шт.'.format(len(params)),
            text_after='добавить/удалить',
            parent=self.action,
            color=lr_lib.core.var.vars_highlight.PopUpWindColor1,
        )
        ans = y.ask()

        # создание param
        if ans == K_FIND:
            params = y.text.split('\n')
            params = lr_lib.core_gui.group_param.gp_filter.param_sort(params, deny_param_filter=False)
            self.after(500, self.destroy)
            lr_lib.core_gui.group_param.core_gp.group_param(None, params, widget=self.action.tk_text, ask=False)
        else:
            return
        return
