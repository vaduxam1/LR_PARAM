# -*- coding: UTF-8 -*-
# grid виджетов action.с окна

import os
import contextlib

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.gui.widj.highlight_text as lr_highlight_text
import lr_lib.core.var.vars as lr_vars


class ActBackup:
    def __init__(self, tk_text, file_bar, id_: int):
        self.backup_entry = tk.Entry(file_bar, font=lr_vars.DefaultFont, width=5, justify='center')
        self.backup_entry.insert('1', lr_vars.BackupActionFile)
        self.tk_text = tk_text
        self.id_ = id_
        self._backup_index = 0

    def backup(self) -> None:
        '''сделать action.c бэкап'''
        self._backup_index += 1

        if self._backup_index > int(self.backup_entry.get()):
            self._backup_index = 1

        d = lr_vars.BackupFolder
        if not os.path.isdir(d):
            os.makedirs(d)
        b_name = self.backup_name()

        with open(b_name, 'w', errors='replace', encoding=lr_vars.VarEncode.get()) as f:
            f.write(self.tk_text.get(1.0, tk.END))

        lr_vars.Logger.debug('{} = {} byte'.format(b_name, os.path.getsize(b_name)))

    def backup_name(self) -> str:
        '''имя backup-файла'''
        return os.path.join(lr_vars.BackupFolder, lr_vars.BackupName.format(i=self.id_, ind=self._backup_index))


class ActScrollText:
    def __init__(self):
        self.tk_text = lr_highlight_text.HighlightText(self, background=lr_vars.Background, wrap=tk.NONE, bd=0)

        self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
        self.tk_text.configure(yscrollcommand=self.report_position_Y, xscrollcommand=self.report_position_X, bd=0)

    def report_position_X(self, *argv) -> None:
        '''get (beginning of) first visible line'''
        self.text_scrollx.set(*argv)
        self.report_position()

    def report_position_Y(self, *argv) -> None:
        '''get (beginning of) first visible line'''
        self.text_scrolly.set(*argv)
        self.report_position()

    def report_position(self) -> None:
        '''при скролле tk.Text, вывести номера линий'''
        top_bottom = (
            int(self.tk_text.index("@0,0").split('.', 1)[0]),
            int(self.tk_text.index("@0,%d" % self.tk_text.winfo_height()).split('.', 1)[0])
        )
        self.tk_text.highlight_lines.set_top_bottom(top_bottom)


class ActSearch:
    def __init__(self, tk_text, toolbar, update: callable):
        self.searchPosVar = tk.StringVar(value='')
        self.searchVar = tk.StringVar(value='')

        self._uptext = '<-up %s'
        self.update = update

        self.tk_text = tk_text

        self.search_entry = ttk.Combobox(toolbar, textvariable=self.searchVar, font=lr_vars.DefaultFont + ' italic',
                                         justify='center')
        self.search_entry.bind("<KeyRelease-Return>", self.search_in_action)
        self.search_entry['values'] = ['']

        self.search_res_combo = ttk.Combobox(toolbar, textvariable=self.searchPosVar, justify='center',
                                             font=lr_vars.DefaultFont, background=lr_vars.Background)

        self.search_res_combo.bind("<<ComboboxSelected>>", self.tk_text_see)
        self.search_res_combo.bind("<KeyRelease-Return>", self.tk_text_see)

        self.up_search_button = tk.Button(toolbar, text=self._uptext, command=self.search_up,
                                          font=lr_vars.DefaultFont)

        self.down_search_button = tk.Button(toolbar, text='down->', command=self.search_down,
                                            font=lr_vars.DefaultFont)

    def search_down(self, *a) -> None:
        '''поиск вниз, по тексту action.c'''
        def func() -> None:
            bhl = self.backgr_butt()
            next(bhl)

            i = len(list(self.search_res_combo['values']))
            if i:
                self._search_index += 1
                if self._search_index >= i:
                    self._search_index = 0

                self.search_res_combo.current(self._search_index)
                self.tk_text_see()
                self.tk_text._on_change()

            next(bhl, None)
        lr_vars.MainThreadUpdater.submit(func)

    def search_up(self, *a) -> None:
        '''поиск вверх, по тексту action.c'''
        def func() -> None:
            bhl = self.backgr_butt()
            next(bhl)

            i = len(list(self.search_res_combo['values']))
            if i:
                self._search_index -= 1
                if self._search_index < 0:
                    self._search_index = i - 1
                self.search_res_combo.current(self._search_index)
                self.tk_text_see()

            next(bhl, None)
        lr_vars.MainThreadUpdater.submit(func)

    def search_in_action(self, *a, word=None, hist=True) -> None:
        '''поиск в tk_text'''
        def func(word=word, hist=hist) -> None:
            if lr_vars.Window._block_:
                return

            bhl = self.backgr_butt()
            next(bhl)
            self._search_index = -1
            self.search_res_combo.set('')

            if word is None:
                word = self.search_entry.get()
            else:
                self.search_entry.set(word)

            if hist:
                vals = list(self.search_entry['values'])
                vals.reverse()
                if word not in vals:
                    self.search_entry['values'] = (vals + [word])
                    self.search_entry.current(0)

            self.search_res_combo['values'] = self._search_text(word=word)
            _, a, b = lr_tooltip.widget_values_counter(self.search_res_combo)
            self.up_search_button['text'] = self._uptext % '{0}/{1}'.format(a, b)

            if not self.search_res_combo['values']:
                return lr_vars.Logger.warning('в action.c тексте не найдено:\nword="{w}"\ntype={t}\nlen={ln}'.format(
                    w=word, t=type(word), ln=(len(word) if hasattr(word, '__len__') else None)), parent=self)
            else:
                self.search_res_combo.current(0)
                self.tk_text_see()

            next(bhl, None)

        lr_vars.MainThreadUpdater.submit(func)

    def tk_text_see(self, *a) -> None:
        '''перейти на позицию в тексте'''
        if lr_vars.Window._block_:
            return
        pos = self.searchPosVar.get()
        if a:  # при ручном выборе из комбобокса поиска, продолжать выбирать кнопками с этого места
            self._search_index = list(self.search_res_combo['values']).index(pos)
        self.tk_text.mark_set("insert", pos)
        self.tk_text.focus_set()
        self.tk_text.see("insert")
        _, a, b = lr_tooltip.widget_values_counter(self.search_res_combo)
        self.up_search_button.config(text=self._uptext % '{0}/{1}'.format(a, b))

    def _search_text(self, *a, word=None, pos='1.0', coord='{i}+{w}c') -> [str, ]:
        '''поиск в tk_text'''
        if lr_vars.Window._block_:
            return []
        if word is None:
            word = self.searchVar.get()
        if word:
            len_word = len(word)
            word_pos = []
            while True:
                idx = self.tk_text.search(word, pos, tk.END)
                if not idx:
                    break
                pos = coord.format(i=idx, w=len_word)
                word_pos.append(pos)
            return word_pos
        else:
            return []

    def backgr_butt(self) -> iter:
        '''менять/вернуть цвет кнопок'''
        if lr_vars.Window._block_:
            try:
                yield
            finally:
                return

        def change() -> None:
            '''менять'''
            self.search_entry.config(font='Arial 7 bold')
            self.down_search_button.config(background='orange')
            self.up_search_button.config(background='orange')
            self.search_res_combo.config(font='Arial 7 bold')
            self.update()

        def restore() -> None:
            '''вернуть'''
            self.search_entry.config(font=lr_vars.DefaultFont)
            self.search_res_combo.config(font=lr_vars.DefaultFont)
            self.down_search_button.config(background='lightgray')
            _, a, b = lr_tooltip.widget_values_counter(self.search_res_combo)
            self.up_search_button.config(text=self._uptext % '{0}/{1}'.format(a, b), background='lightgrey')
            self.update()

        try:
            lr_vars.Window.after(10, change)
            yield
        finally:
            lr_vars.Window.after(100, restore)
            return


class ActBlock:
    def __init__(self, tk_text, update: callable):
        self.tk_text = tk_text
        self.update = update

    @contextlib.contextmanager
    def block(self, w=('tk_text', 'unblock', 'search_entry', 'search_res_combo', 'toolbar', ), no_highlight=False) -> iter:
        '''заблокировать/разблокировать виджеты в gui'''
        highlight = self.tk_text.highlight_var.get()
        if no_highlight:  # откл подсветку
            self.tk_text.highlight_var.set(False)
        try:
            yield self._block(True, w=w)
        finally:
            self._block(False, w=w)
            if no_highlight:  # вкл подсветку
                self.tk_text.highlight_var.set(highlight)
                self.tk_text.action.tk_text.set_highlight()

    def _block(self, bl: bool, w=()) -> None:
        '''заблокировать/разблокировать виджеты в gui'''
        def set_block(state=('disabled' if bl else 'normal')):
            '''заблокировать/разблокировать'''
            for attr in dir(self):
                if not attr.startswith('_') and (attr not in w):
                    with contextlib.suppress(AttributeError, tk.TclError):
                        getattr(self, attr).configure(state=state)
            self.update()

        lr_vars.MainThreadUpdater.submit(set_block)


def get_action_file(file='action.c') -> str:
    '''найти action.c'''
    if os.path.isfile(file):
        return file
    else:
        action_file = os.path.join(lr_vars.VarFilesFolder.get(), file)
        if os.path.isfile(action_file):
            return action_file
        else:
            return ''


tta = '{p:>3}%\n\npool:\n\n{pt}\n\n{pm}'.format
ttt1 = 'T/qi\n{t}\n{q_in}'.format
ttt2 = 'T={t}'.format
ttm1 = 'M/qi\n{mp}\n{q_in}'.format
ttm2 = 'M={mp}'.format
ttl = '{txt} lines[{top}:{bottom}] | {v} | undo(ctrl-z)/redo(ctrl-y)'.format
restart = lr_vars.Tk.after
ver = lr_vars.VERSION


def auto_update_action_info_lab(self, config, tk_kext, id_: int, timeout: int, check_run: callable, title: callable,
                                _set_title: callable) -> None:
    '''обновление action.label с процентами и пулом'''
    if not check_run(id_):
        return

    highlight_lines = tk_kext.highlight_lines
    (top, bottom) = highlight_lines.on_srean_line_nums
    title(ttl(txt=_set_title(), top=top, bottom=bottom, v=ver))

    tpl = lr_vars.T_POOL
    try:
        pt = ttt1(q_in=tpl.pool._qsize, t=tpl._size)
    except AttributeError:  # tpl.pool._qsize
        pt = ttt2(t=tpl._size)

    mpl = lr_vars.M_POOL
    try:
        pm = ttm1(q_in=mpl.pool._qsize, mp=mpl._size)
    except AttributeError:  # mpl.pool._qsize
        pm = ttm2(mp=mpl._size)

    config(text=tta(p=round(int(tk_kext.linenumbers.linenum) // highlight_lines._max_line_proc), pt=pt, pm=pm))

    # перезапуск
    restart(timeout, auto_update_action_info_lab, self, config, tk_kext, id_, timeout, check_run, title, _set_title)
