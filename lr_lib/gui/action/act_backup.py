# -*- coding: UTF-8 -*-
# action.с окно - бекап

import os
import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.etc.vars_other
import lr_lib.gui.action.act_block
from lr_lib.gui.etc.color_progress import progress_decor


class ActBackup(lr_lib.gui.action.act_block.ActBlock):
    """
    бекап action
        main_action.ActionWindow
        act_win.ActWin
        act_any.ActAny
        act_goto.ActGoto
        act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
        act_serializ.TkTextWebSerialization
      + act_backup.ActBackup
        act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
        act_var.ActVar
        act_toplevel.ActToplevel
        tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_block.ActBlock.__init__(self)
        self._backup_index = 0

        # Entry
        self.backup_entry = tk.Entry(self.file_bar, font=lr_vars.DefaultFont, width=5, justify='center')
        self.backup_entry.insert('1', lr_vars.BackupActionFile)
        return

    @progress_decor
    def backup(self, errors='replace') -> None:
        """
        сделать action.c бэкап
        """
        self._backup_index += 1

        if self._backup_index > int(self.backup_entry.get()):
            self._backup_index = 1

        d = lr_vars.BackupFolder
        if not os.path.isdir(d):
            os.makedirs(d)
        b_name = self.backup_name()

        with open(b_name, 'w', errors=errors, encoding=lr_lib.core.var.etc.vars_other.VarEncode.get()) as f:
            f.write(self.tk_text.get(1.0, tk.END))

        lr_vars.Logger.debug('{} = {} byte'.format(b_name, os.path.getsize(b_name)))
        return

    def backup_name(self) -> str:
        """
        имя backup-файла
        """
        n = lr_vars.BackupName.format(i=self.id_, ind=self._backup_index, )
        i = os.path.join(lr_vars.BackupFolder, n)
        return i

    def destroy(self) -> None:
        """
        выход
        """
        try:
            self.backup()
        except AttributeError as ex:
            pass
        try:
            del lr_vars.Window.action_windows[self.id_]
        except KeyError as ex:
            pass

        super().destroy()
        return
