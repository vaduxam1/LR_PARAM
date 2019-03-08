# -*- coding: UTF-8 -*-
# окно ячейка Настраиваемый запуск поиска WRSP
import tkinter as tk
from typing import Iterable, Tuple, List, Callable

import lr_lib
from lr_lib.core.var.etc.vars_other import T_POOL_decorator
from lr_lib.core_gui.run.r_other import set_state_widg, block
from lr_lib.gui.etc.color_progress import progress_decor

ColorHide = 'black'


class RItem:
    """
    gui виджет метода поиска
    """

    def __init__(self,
                 parent: 'lr_lib.core_gui.run.run_setting.RunSettingWindow',
                 function: Callable,
                 main_label: str,
                 _act_num=1,
                 files_req=True,
                 files_resp=True,
                 files_other=False,
                 only_in_act_param=True,
                 label_title='',
                 enable=True,
                 kwargs=None,
                 ):
        self.parent = parent

        self.kwargs = {}
        if kwargs:
            self.kwargs.update(kwargs)

        self._function = function
        self.function = progress_decor(self._function, self)

        # LabelFrame
        self.main_label = tk.LabelFrame(
            self.parent.main_label, text=main_label, font='Arial 8 bold', fg='blue', labelanchor=tk.NW, bd=5,
        )

        # LabelFrame
        tt_sl = 'поиск {param} производить в:'
        self.search_label = tk.LabelFrame(
            self.main_label, text=tt_sl, font='Arial 7', fg=ColorHide,
        )

        # LabelFrame Action
        tt_sa = 'action.c:'
        self.search_label_act = tk.LabelFrame(
            self.search_label, text=tt_sa, font='Arial 7 bold',
        )

        # LabelFrame Файлы
        tt_sf = '\\data\\ файлах:'
        self.search_label_files = tk.LabelFrame(
            self.search_label, text=tt_sf, font='Arial 7 bold',
        )

        # Radiobutton StringVar
        self.act_radio = tk.StringVar(value='web')

        # Radiobutton
        self._a1 = 'весь action текст'
        _a1 = 'all_action'
        self.rad_act_all = tk.Radiobutton(
            self.search_label_act, text=self._a1, font='Arial 7', justify='left', fg=ColorHide,
            variable=self.act_radio, value=_a1,
        )
        tt8 = 'Поиск {param}, внутри всего текста,\n"Action.c" файла.'
        lr_lib.gui.widj.tooltip.createToolTip(self.rad_act_all, tt8)

        # Radiobutton
        self._a2 = 'тела любых web_ объектов'
        _a2 = 'web'
        self.rad_act_any = tk.Radiobutton(
            self.search_label_act, text=self._a2, font='Arial 7', justify='left', fg=ColorHide,
            variable=self.act_radio, value=_a2,
        )
        tt9 = 'Поиск {param}, только внутри,\nтел web_ объектов,\n"Action.c" файла.'
        lr_lib.gui.widj.tooltip.createToolTip(self.rad_act_any, tt9)

        # Radiobutton
        self._a3 = 'тела web_.snapshot объектов'
        _a3 = 'snapshot'
        self.rad_act_snap = tk.Radiobutton(
            self.search_label_act, text=self._a3, font='Arial 7', justify='left', fg=ColorHide,
            variable=self.act_radio, value=_a3,
        )
        tt10 = 'Поиск {param}, только внутри,\nтел web_ объектов имеющих snapshot,\n"Action.c" файла.'
        lr_lib.gui.widj.tooltip.createToolTip(self.rad_act_snap, tt10)

        # Radiobutton
        self._a4 = 'не искать в action.c файле.'
        _a4 = 'None'
        self.rad_act_no_act = tk.Radiobutton(
            self.search_label_act, text=self._a4, font='Arial 7', justify='left', fg=ColorHide,
            variable=self.act_radio, value=_a4,
        )
        tt11 = 'Не искать {param} внутри "Action.c" файла.'
        lr_lib.gui.widj.tooltip.createToolTip(self.rad_act_no_act, tt11)

        # Checkbutton
        tt_fq = 'Request'
        self._cbx_req = tk.BooleanVar(value=files_req)
        self.cbx_req = tk.Checkbutton(
            self.search_label_files, text=tt_fq, font='Arial 7', justify='left', fg=ColorHide,
            variable=self._cbx_req,
        )
        tt5 = 'Поиск {param} только в "Request" файлах каталога "data".'
        lr_lib.gui.widj.tooltip.createToolTip(self.cbx_req, tt5)

        # Checkbutton
        tt_fr = 'Response'
        self._cbx_resp = tk.BooleanVar(value=files_resp)
        self.cbx_resp = tk.Checkbutton(
            self.search_label_files, text=tt_fr, font='Arial 7', justify='left', fg=ColorHide,
            variable=self._cbx_resp,
        )
        tt6 = 'Поиск {param} только в "Response" файлах каталога "data".'
        lr_lib.gui.widj.tooltip.createToolTip(self.cbx_resp, tt6)

        # Checkbutton
        tt_fo = 'Любые другие'
        self._cbx_other = tk.BooleanVar(value=files_other)
        self.cbx_other = tk.Checkbutton(
            self.search_label_files, text=tt_fo, font='Arial 7', justify='left', fg=ColorHide,
            variable=self._cbx_other,
        )
        tt7 = 'Поиск {param} в любых файлах каталога "data", но не в "Request\Response" файлах.\n\n' \
              'Тут могут быть файлы ответов, ошибочно неиспользуемые утилитой.\n' \
              'Или какие-то логи, где {param} упоминается в другом контексте,\nи отсюда его уже можно вытащить.\n' \
              'В том числе тут есть копии оригинальных actions.c / vuser_end.c / vuser_init.c'
        lr_lib.gui.widj.tooltip.createToolTip(self.cbx_other, tt7)

        # Button
        tt_be = 'настраиваемый поиск и создание {param}'
        self.btn_edit = tk.Button(
            self.main_label, font='Arial 7', text=tt_be, padx=0, pady=0, relief='groove',
            command=lambda: T_POOL_decorator(self.get_params)(ask=True, ask2=True, wrsp_create=True),
        )
        tt4 = 'Поиск и создание {param} "вручную" данным методом,\nс возможностью выбрать настройки поиска.'
        lr_lib.gui.widj.tooltip.createToolTip(self.btn_edit, tt4)

        # Button
        tt_br = 'предпросмотр'
        self.btn_run = tk.Button(
            self.search_label, font='Arial 7', text=tt_br, padx=0, pady=0, relief='groove',
            command=lambda: T_POOL_decorator(self.get_params)(ask=False, ask2=True, wrsp_create=False),
        )
        tt3 = 'Поиск и просмотр {param},\nкоторые найдет этот метод поиска,\n' \
              'с настройками по умолчанию.\nКнопка "Запуск" найдет теже {param}.'
        lr_lib.gui.widj.tooltip.createToolTip(self.btn_run, tt3)

        # Checkbutton
        tt_iap = 'Отсеять {param}, ненайденные в action'
        self._cbx_only_in_act_param = tk.BooleanVar(value=only_in_act_param)
        self.cbx_only_in_act_param = tk.Checkbutton(
            self.search_label, text=tt_iap, font='Arial 7', justify='left',
            variable=self._cbx_only_in_act_param, fg=ColorHide,
        )
        tt1 = 'В файлах ответов можно найти множество {param},\nкоторые не используются внутри "Action.c" файла.\n' \
              'Такие {param} создавать бесполезно.'
        lr_lib.gui.widj.tooltip.createToolTip(self.cbx_only_in_act_param, tt1)

        # Checkbutton
        tt_on = 'Вкл. / Выкл.'
        self._cbx_on = tk.BooleanVar(value=enable)
        disable_widg = [self.search_label_files, self.search_label_act, ]
        disable_widg.extend(self.main_label.winfo_children())
        cmd = set_state_widg(self._cbx_on, disable_widg)
        self.cbx_on = tk.Checkbutton(
            self.main_label, text=tt_on, font='Arial 8 bold', justify='left', fg=ColorHide, variable=self._cbx_on,
            command=cmd,
        )
        cmd()  # заблокировать откл методы поиска
        tt2 = 'вкл/выкл использование метода поиска {param}\n'
        tt2 += label_title
        lr_lib.gui.widj.tooltip.createToolTip(self.cbx_on, tt2)

        # grid
        self.rad_act_all.grid(row=8, column=2, sticky=tk.W)
        self.rad_act_any.grid(row=7, column=2, sticky=tk.W)
        self.rad_act_snap.grid(row=6, column=2, sticky=tk.W)
        self.rad_act_no_act.grid(row=5, column=2, sticky=tk.W)

        self.cbx_req.grid(row=5, column=1, sticky=tk.W)
        self.cbx_resp.grid(row=6, column=1, sticky=tk.W)
        self.cbx_other.grid(row=7, column=1, sticky=tk.W)

        self.cbx_on.grid(row=0, column=1, sticky=tk.W)

        self.btn_edit.grid(row=0, column=2, sticky=tk.NSEW)

        self.btn_run.grid(row=10, column=1, sticky=tk.NSEW)
        self.cbx_only_in_act_param.grid(row=10, column=2, sticky=tk.W)

        self.search_label.grid(row=5, column=1, sticky=tk.W, columnspan=3)
        self.search_label_files.grid(row=5, column=1, sticky=tk.NSEW)
        self.search_label_act.grid(row=5, column=2, sticky=tk.NSEW)

        #
        self.block_items = [self.main_label, ]
        self._is_block_ = False
        #
        self.act_radio_vals = [_a1, _a2, _a3, _a4, ]
        a = self.act_radio_vals[_act_num]
        self.act_radio.set(a)
        return

    def get_params(self, ask=False, ask2=False, wrsp_create=False, i_params=None) -> List[str]:
        """
        получить params
        """
        if not self._cbx_on.get():
            return []

        if i_params is None:
            i_params = set()

        only_in_act = self._cbx_only_in_act_param.get()

        with block(self):
            ps = self.get_params_source()

            params = self.function(
                self.parent.action,
                ps,
                ask=ask,
                ask2=ask2,
                wrsp_create=wrsp_create,
                action_text=only_in_act,
                i_params=i_params,
                **self.kwargs
            )
        return params

    def get_params_source(self) -> List:
        """
        найти params_source
        """
        vals = []

        act_var = self.act_radio.get()
        if act_var != 'None':
            item = [act_var, self.parent.action]
            vals.append(item)

        cbx = [self._cbx_req, self._cbx_resp, self._cbx_other, ]
        states = ['Request', 'Response', 'any', ]
        for (cb, st) in zip(cbx, states):
            if cb.get():
                vals.append(st)
            continue

        return vals

    def search_label_text(self, add: int, new: int) -> None:
        """
        сколько param, нашел конкретный метод поиска
        """
        t = self.search_label['text']
        t = t.split(':', 1)[0]
        t += ': найдено:{add} шт, новых:{new} шт.'.format(add=add, new=new,)
        self.search_label['text'] = t
        return
