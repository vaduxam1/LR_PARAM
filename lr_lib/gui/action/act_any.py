﻿# -*- coding: UTF-8 -*-
# action.с окно - всякое

import os
import time
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_param
import lr_lib.gui.action.act_goto


class ActAny(lr_lib.gui.action.act_goto.ActGoto):
    """
    разное
        main_action.ActionWindow
        act_win.ActWin
      + act_any.ActAny
        act_goto.ActGoto
        act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
        act_serializ.TkTextWebSerialization
        act_backup.ActBackup
        act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
        act_var.ActVar
        act_toplevel.ActToplevel
        tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_goto.ActGoto.__init__(self)
        return

    def widj_reset(self) -> None:
        """
        обновить виджеты
        """
        super().widj_reset()
        self.transaction_combo_set()

        self.inf_combo_set()
        self.toolbar['text'] = self.param_counter(all_param_info=False)
        self.set_title()
        self.set_combo_len()
        return

    def param_counter(self, all_param_info=False) -> str:
        """
        подсчитать кол-во созданных web_reg_save_param
        """
        self.wrsp_combo_set()
        self.param_combo_set()
        if all_param_info:
            lr_vars.Logger.debug(self.web_action.websReport.web_snapshot_param_in_count)

        i = 'всего web_reg_save_param : {w}'.format(w=len(self.web_action.websReport.wrsp_and_param_names))
        return i

    def clear_text(self) -> None:
        """
        очистить tk_text
        """
        if tkinter.messagebox.askquestion('очистить', 'очистить окно?', parent=self) == 'yes':
            self.backup()
            self.tk_text.delete(1.0, tk.END)

    def set_combo_len(self):
        """
        задать ширину всех ['values'] виджетов
        """
        if lr_vars.Window._block_:
            return

        min_len = lr_vars.VarActComboLenMin.get()
        max_len = lr_vars.VarActComboLenMax.get()

        for w in dir(self):
            attr = getattr(self, w)
            if isinstance(attr, ttk.Combobox):
                m = max([len(str(f)) for f in attr['values']] or [min_len])
                attr.configure(width=m if (min_len <= m <= max_len) else (min_len if (m < min_len) else max_len))
            continue

        self.selection_font_combo.configure(width=20)
        self.font_combo.configure(width=20)
        return

    def set_title(self) -> None:
        """
        main title
        """
        t = '{} {} undo: ctrl-z / redo: ctrl-y)'.format(self._set_title(), lr_vars.VERSION,)
        self.title(t)
        return

    def _set_title(self) -> str:
        """
        main title
        """
        i = '{a} | {i} | backup={b} | Всего( WRSP/WebSnapshot/WebAny ) : ( {ww}/{ws}/{wa} ) |'.format(
            a=self.action_file,
            b=self._backup_index,
            i=self.id_,
            ww=len(self.web_action.websReport.wrsp_and_param_names),
            wa=len(list(self.web_action.get_web_all())),
            ws=len(list(self.web_action.get_web_snapshot_all())),
        )
        return i

    def _open_action_final(self, *args) -> None:
        """
        сообщения и действия, после открытия нового action файла
        """
        if not self.action_file:
            return

        info = []
        t = time.strftime('%H:%M:%S %m.%d.%y', time.gmtime(os.path.getmtime(self.action_file)))
        e = '{f} : size={sa}, id={s}, create={t}'
        a = e.format(f=self.action_file, s=self.id_, sa=os.path.getsize(self.action_file), t=t,)
        info.append(a)

        if self.web_action.websReport.rus_webs:
            s = 'В следующих номерах inf, обнаружены Русские(NoASCII) символы, ' \
                'возможно требуется перекодировка(выделение/encoding из меню мыши)\n{}'
            b = s.format(self.web_action.websReport.rus_webs)
            info.append(b)

        if self.web_action.websReport.google_webs:
            r = 'Возможно следующие номера inf лишние, тк содержат слова {s}\nих можно удалить' \
                '(+"сохр пользоват. измения в тексте" из меню мыши)\n{w}'
            d = r.format(w=self.web_action.websReport.google_webs, s=lr_lib.core.var.vars_param.DENY_WEB_)
            info.append(d)

        if info:
            lr_vars.Logger.info('\n\n'.join(info), parent=self)
        return
