# -*- coding: UTF-8 -*-
# action.с окно - преобразование action-текста(tk_text) во внутреннее представление(web_action), и обратно"

import os
import glob
import tkinter as tk
import tkinter.messagebox
from typing import Dict, List

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.etc.vars_other
import lr_lib.core.wrsp.param
import lr_lib.gui.action._other
import lr_lib.gui.action.act_backup
import lr_lib.gui.etc.gui_other
from lr_lib.gui.etc.color_progress import progress_decor


class TkTextWebSerialization(lr_lib.gui.action.act_backup.ActBackup):
    """
    преобразование action-текста(tk_text) во внутреннее представление(web_action), и обратно
        main_action.ActionWindow
        act_win.ActWin
        act_any.ActAny
        act_goto.ActGoto
        act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
      + act_serializ.TkTextWebSerialization
        act_backup.ActBackup
        act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
        act_var.ActVar
        act_toplevel.ActToplevel
        tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_backup.ActBackup.__init__(self)

        # Button
        cmd = lambda *a: self.open_action_dialog(title=True, folder=lr_vars.BackupFolder)
        self.backup_open_button = tk.Button(
            self.file_bar, text='backup_open', background='orange', font=(lr_vars.DefaultFont + ' bold'),
            command=cmd,
        )

        # Button
        self.save_action_button = tk.Button(
            self.file_bar, text='save', font=(lr_vars.DefaultFont + ' bold'), command=self.save_action_file,
        )

        # Button
        self.open_button = tk.Button(
            self.file_bar, text='open', font=lr_vars.DefaultFont, command=self.open_action_dialog,
        )
        return

    @progress_decor
    def web_action_to_tk_text(self, websReport=False, highlight_apply=True, gui_reset=True) -> None:
        """
        from self.web_action to self.tk_text
        """
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
        """
        from self.tk_text to self.web_action
        """
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
    def open_action(self, file=None, callback=None) -> None:
        """
        сформировать vuser_init.c/action.c/.../vuser_end.c
        """
        if file:
            enc = lr_lib.core.var.etc.vars_other.VarEncode.get()
            with open(file, errors='replace', encoding=enc) as f:
                text = f.read()
            self.tk_text_to_web_action(text=text, websReport=True)
            if callback:
                callback()
            return

        # из usr файла
        try:
            usr_files = glob.glob('*.usr')
            # открыть все vuser_init.c/action.c/.../vuser_end.c
            if len(usr_files) > 1:  # по умолчению, должен быть только один
                name = os.path.split(os.getcwd())[1]  # имя текущего каталога
                usr_ = '{}.usr'.format(name)  # {одноименно с каталогом}.usr
                usr = [n for n in usr_files if (n == usr_)][0]
            elif len(usr_files) == 1:
                usr = usr_files[0]
            else:
                raise UserWarning  # только только action.c

            c_files = {}
            need_lines = False

            with open(usr) as f:  # не использовать configparser, т.к. вроде он падает, на каких-то .usr файлах (может там не соблюдается ini формат?)
                for line in map(str.strip, f):
                    if need_lines:
                        if line.startswith('['):  # [Recorded Actions] - далее ненужно
                            break
                    else:
                        need_lines = (line == '[Actions]')  # нужно, с этого момента

                    if need_lines and line.endswith('.c') and ('=' in line):
                        (category, file) = line.split('=', 1)
                        c_files[category] = file
                    continue

            self.tk_text_to_web_action(text=lr_texts_join(c_files), websReport=True)
            if callback:
                callback()

        except Exception as ex:
            self.open_action_force(callback=callback)  # открыть только action.c
        return

    @progress_decor
    def open_action_force(self, callback=None) -> None:
        """
        сформировать только action.c
        """
        c_files = {
            'vuser_init': 'vuser_init.c',
            'Action': 'Action.c',
            'vuser_end': 'vuser_end.c',
        }
        s = 'Будут открыты только {f} файла:\n{fs} .\nНеобходимо проверить, что не используются другие action файлы.' \
            '\nВ директории утилиты должен присутствовать файл: "<одноименно с каталогом>.usr"'
        tkinter.messagebox.showwarning('Внимание', s.format(f=len(c_files), fs=str(list(c_files.values())),),
                                       parent=self)
        self.tk_text_to_web_action(text=lr_texts_join(c_files), websReport=True)
        if callback:
            callback()
        return

    @progress_decor
    def save_action_file(self, file_name=None, errors='replace', websReport=True) -> None:
        """
        текст to WEB_ACTION - сохранить текст action.c окна
        """
        self.tk_text_to_web_action(websReport=websReport)

        if file_name is None:
            file_name = tk.filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                filetypes=(("action.c", "*.c"), ("all", "*.*")),
                title='сохранить текст action.c окна',
                parent=self,
            )
        if file_name:
            with open(file_name, 'w', errors=errors, encoding=lr_lib.core.var.etc.vars_other.VarEncode.get()) as act:
                act.write(self.tk_text.get(1.0, tk.END))
        return

    def open_action_dialog(self, *a, title=False, folder=os.getcwd()) -> None:
        """
        открыть файл
        """
        if title:
            ft = (("%s_backup_*.c" % self.id_, "%s_backup_*.c" % self.id_), ("all", "*.*"))
            af = tk.filedialog.askopenfilename(
                initialdir=folder, parent=self, filetypes=ft, title='backup({})'.format(self.id_)
            )
        else:
            af = tk.filedialog.askopenfilename(
                initialdir=folder, parent=self, filetypes=(("action.c", "*.c"), ("all", "*.*"))
            )
        if af:
            self.open_action(file=af)
        return

    def show_info(self) -> None:
        """
        всякая инфа
        """
        len_all_files = len(lr_vars.AllFiles)
        all_infs = len(list(lr_lib.core.etc.other.get_files_infs(lr_vars.AllFiles)))

        lr_vars.Window.last_frame['text'] = "snapshots: {i} inf's | файлов: {f} | {d}".format(
            d=lr_vars.VarFilesFolder.get(), f=len_all_files, i=all_infs)

        any_w = len(tuple(self.web_action.get_web_all()))
        sn_w = len(self.web_action.action_infs)
        files = len([f for f in lr_vars.AllFiles if any(map(
            self.web_action.action_infs.__contains__, f['Snapshot']['Nums']))])

        dsnap_w = len(self.web_action.drop_infs)
        dfiles = len(self.web_action.drop_files)

        t = "action.c web_* : любых={any_w}, (Snapshot's / файлов_ответов) = ({snap_w} / {files}) |" \
            " Удалено: ({dsnap_w} / {dfls})".format(any_w=any_w, snap_w=sn_w, files=files, dsnap_w=dsnap_w, dfls=dfiles)
        self.middle_bar['text'] = t

        if self.web_action.drop_infs or self.web_action.drop_files:
            i = 'action.c: Удалено: inf: {il}, файлов : {fl} | Найдено: {ai} inf'.format(il=dsnap_w, fl=dfiles, ai=sn_w)
            lr_vars.Logger.debug(i, parent=self)
        return

    def widj_reset(self) -> None:
        """
        обновить виджеты
        """
        self.transaction.clear()
        self.transaction.extend(lr_lib.gui.etc.gui_other.get_transaction(self.tk_text.get(1.0, tk.END)))
        return


SPL = '\n{c} ->\n{c} %s\n{c} <-\n'.format(c='// {}'.format('~' * 15))  # lr_lib.core.wrsp.param.LR_COMENT


def lr_texts_join(c_files: Dict) -> str:
    """объединить текст нескольких .c файлов"""
    enc = lr_lib.core.var.etc.vars_other.VarEncode.get()
    text = ''.join('{cm}\n{f}'.format(
        f=open(c_files[cat], errors='replace', encoding=enc).read(),
        cm=(SPL % cat),
    ) for cat in c_files)
    return text
