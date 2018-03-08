# -*- coding: UTF-8 -*-
# action.с окно - всякое

import os
import time

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.action.act_goto as lr_act_goto


class ActAny(lr_act_goto.ActGoto):
    """разное"""

    def __init__(self):
        lr_act_goto.ActGoto.__init__(self)

    def widj_reset(self) -> None:
        """обновить виджеты"""
        super().widj_reset()
        self.transaction_combo_set()

        self.inf_combo_set()
        self.toolbar['text'] = self.param_counter(all_param_info=False)
        self.set_title()
        self.set_combo_len()

    def param_counter(self, all_param_info=False) -> str:
        """подсчитать кол-во созданных web_reg_save_param"""
        self.wrsp_combo_set()
        self.param_combo_set()

        if all_param_info:
            lr_vars.Logger.debug(self.web_action.websReport.web_snapshot_param_in_count)
        return 'всего web_reg_save_param : {w}'.format(w=len(self.web_action.websReport.wrsp_and_param_names))

    def clear_text(self) -> None:
        """очистить tk_text"""
        if messagebox.askquestion('очистить', 'очистить окно?', parent=self) == 'yes':
            self.backup()
            self.tk_text.delete(1.0, tk.END)

    def set_combo_len(self):
        """задать ширину всех ['values'] виджетов"""
        if lr_vars.Window._block_:
            return

        min_len = lr_vars.VarActComboLenMin.get()
        max_len = lr_vars.VarActComboLenMax.get()

        for w in dir(self):
            attr = getattr(self, w)
            if isinstance(attr, ttk.Combobox):
                m = max([len(str(f)) for f in attr['values']] or [min_len])
                attr.configure(width=m if (min_len <= m <= max_len) else (min_len if (m < min_len) else max_len))

        self.selection_font_combo.configure(width=20)
        self.font_combo.configure(width=20)

    def set_title(self) -> None:
        self.title('{} {} undo: ctrl-z / redo: ctrl-y)'.format(self._set_title(), lr_vars.VERSION))

    def _set_title(self) -> str:
        return '{a} | {i} | backup={b} |'.format(a=self.action_file, b=self._backup_index, i=self.id_)

    def _open_action_final(self, *args) -> None:
        """сообщения и действия, после открытия нового action файла"""
        if not self.action_file:
            return

        info = []
        t = time.strftime('%H:%M:%S %m.%d.%y', time.gmtime(os.path.getmtime(self.action_file)))
        info.append('{f} : size={sa}, id={s}, create={t}'.format(
            f=self.action_file, s=self.id_, sa=os.path.getsize(self.action_file), t=t))

        if self.web_action.websReport.rus_webs:
            info.append('В следующих номерах inf, обнаружены Русские(NoASCII) символы, возможно требуется '
                        'перекодировка(выделение/encoding из меню мыши)\n{}'.format(
                self.web_action.websReport.rus_webs))

        if self.web_action.websReport.google_webs:
            info.append('Возможно следующие номера inf лишние, тк содержат слова {s}\nих можно удалить('
                        '+"сохр пользоват. измения в тексте" из меню мыши)\n{w}'.format(
                w=self.web_action.websReport.google_webs, s=lr_vars.DENY_WEB_))

        if info:
            lr_vars.Logger.info('\n\n'.join(info), parent=self)
