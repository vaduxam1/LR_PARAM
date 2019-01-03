# -*- coding: UTF-8 -*-
# action.с окно - преобразование action-текста(tk_text) во внутреннее представление(web_action), и обратно"

import os

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars_other
import lr_lib.gui.etc.gui_other
import lr_lib.gui.action._other
import lr_lib.gui.action.act_backup
import lr_lib.core.var.vars as lr_vars
from lr_lib.gui.etc.color_progress import progress_decor


class TkTextWebSerialization(lr_lib.gui.action.act_backup.ActBackup):
    """преобразование action-текста(tk_text) во внутреннее представление(web_action), и обратно"""

    def __init__(self):
        lr_lib.gui.action.act_backup.ActBackup.__init__(self)

        self.backup_open_button = tk.Button(
            self.file_bar, text='backup_open', background='orange', font=lr_vars.DefaultFont + ' bold',
            command=lambda *a: self.open_action_dialog(title=True, folder=lr_vars.BackupFolder))

        self.save_action_button = tk.Button(
            self.file_bar, text='save', font=lr_vars.DefaultFont + ' bold', command=self.save_action_file)

        self.open_button = tk.Button(
            self.file_bar, text='open', font=lr_vars.DefaultFont, command=self.open_action_dialog)
        return

    @progress_decor
    def web_action_to_tk_text(self, websReport=False, highlight_apply=True, gui_reset=True) -> None:
        """from self.web_action to self.tk_text"""
        text = self.web_action.to_str(websReport=websReport)
        self.tk_text.new_text_set(text)

        if gui_reset:
            self.show_info()
            self.widj_reset()
            lr_vars.Window.setSortKeys()
            lr_vars.Window.set_maxmin_inf(lr_vars.AllFiles)

        if highlight_apply:  # подсветка текста, при изменении
            self.tk_text.highlight_apply()
        return

    @progress_decor
    def tk_text_to_web_action(self, text=None, websReport=True, highlight_apply=True, gui_reset=True) -> None:
        """from self.web_action to self.tk_text"""
        if text is None:
            text = self.tk_text.get(1.0, tk.END)

        # сохранить позицию с тексте, перед его заменой
        pos = self.tk_text.cursor_position

        self.web_action.set_text_list(text, websReport=websReport)
        self.web_action_to_tk_text(websReport=False, highlight_apply=highlight_apply, gui_reset=gui_reset)

        # востановить позицию с тексте
        self.tk_text.mark_set("insert", pos)
        self.tk_text.focus_set()
        self.tk_text.see("insert")
        return

    @progress_decor
    def open_action(self, file=None, errors='replace', callback=None) -> None:
        """сформировать action.c"""
        self.action_file = file or lr_lib.gui.action._other.get_action_file(lr_vars.VarFilesFolder.get())

        if os.path.isfile(self.action_file):
            with open(self.action_file, errors=errors, encoding=lr_lib.core.var.vars_other.VarEncode.get()) as text:
                self.tk_text_to_web_action(text=text, websReport=True)
            if callback:
                callback()
        return

    @progress_decor
    def save_action_file(self, file_name=None, errors='replace', websReport=True) -> None:
        """текст to WEB_ACTION - сохранить текст action.c окна"""
        self.tk_text_to_web_action(websReport=websReport)

        if file_name is None:
            file_name = tk.filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                filetypes=(("action.c", "*.c"), ("all", "*.*")),
                title='сохранить текст action.c окна',
                parent=self,
            )
        if file_name:
            with open(file_name, 'w', errors=errors, encoding=lr_lib.core.var.vars_other.VarEncode.get()) as act:
                act.write(self.tk_text.get(1.0, tk.END))
        return

    def open_action_dialog(self, *a, title=False, folder=os.getcwd()) -> None:
        """открыть файл"""
        if title:
            af = tk.filedialog.askopenfilename(initialdir=folder, parent=self, filetypes=(
                ("%s_backup_*.c" % self.id_, "%s_backup_*.c" % self.id_), ("all", "*.*")),
                                               title='backup({})'.format(self.id_))
        else:
            af = tk.filedialog.askopenfilename(initialdir=folder, parent=self, filetypes=(
                ("action.c", "*.c"), ("all", "*.*")))
        if af:
            self.open_action(file=af)
        return

    def show_info(self) -> None:
        """всякая инфа"""
        len_all_files = len(lr_vars.AllFiles)
        all_infs = len(list(lr_lib.core.etc.other.get_files_infs(lr_vars.AllFiles)))

        lr_vars.Window.last_frame['text'] = "snapshots: {i} inf's | файлов: {f} | {d}".format(
            d=lr_vars.VarFilesFolder.get(), f=len_all_files, i=all_infs)

        any_w = len(tuple(self.web_action.get_web_all()))
        snap_w = len(self.web_action.action_infs)
        files = len([f for f in lr_vars.AllFiles if any(map(
            self.web_action.action_infs.__contains__, f['Snapshot']['Nums']))])

        dsnap_w = len(self.web_action.drop_infs)
        dfiles = len(self.web_action.drop_files)

        t = "action.c web_* : любых={any_w}, (Snapshot's / файлов_ответов) = ({snap_w} / {files}) |" \
            " Удалено: ({dsnap_w} / {dfiles})".format(
            any_w=any_w, snap_w=snap_w, files=files, dsnap_w=dsnap_w, dfiles=dfiles)
        self.middle_bar['text'] = t

        if self.web_action.drop_infs or self.web_action.drop_files:
            lr_vars.Logger.debug('Удалено в action.c: inf: {il}, файлов : {fl} | Найдено: {ai} inf'.format(
                il=dsnap_w, fl=dfiles, ai=snap_w), parent=self)
        return

    def widj_reset(self) -> None:
        """обновить виджеты"""
        self.transaction.clear()
        self.transaction.extend(lr_lib.gui.etc.gui_other.get_transaction(self.tk_text.get(1.0, tk.END)))
        return
