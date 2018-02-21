# -*- coding: UTF-8 -*-
# action.с окно - поиск текста

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import messagebox

import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.gui.action.act_serializ as lr_act_serializ
import lr_lib.core.var.vars as lr_vars


class ActSearch(lr_act_serializ.TkTextWebSerialization):
    """поиск текста"""

    def __init__(self):
        lr_act_serializ.TkTextWebSerialization.__init__(self)

        self._search_index = -1

        self.searchPosVar = tk.StringVar(value='')
        self.searchVar = tk.StringVar(value='')

        self._uptext = '<-up %s'

        self.search_button = tk.Button(
            self.toolbar, text='> Поиск >', command=self.search_in_action, font=lr_vars.DefaultFont)
        self.search_entry = ttk.Combobox(
            self.toolbar, textvariable=self.searchVar, font=lr_vars.DefaultFont + ' italic', justify='center')
        self.search_entry.bind("<KeyRelease-Return>", self.search_in_action)
        self.search_entry['values'] = ['']

        self.search_res_combo = ttk.Combobox(
            self.toolbar, textvariable=self.searchPosVar, justify='center', font=lr_vars.DefaultFont,
            background=lr_vars.Background)

        self.search_res_combo.bind("<<ComboboxSelected>>", self.tk_text_see)
        self.search_res_combo.bind("<KeyRelease-Return>", self.tk_text_see)

        self.up_search_button = tk.Button(
            self.toolbar, text=self._uptext, command=self.search_up, font=lr_vars.DefaultFont)

        self.down_search_button = tk.Button(
            self.toolbar, text='down->', command=self.search_down, font=lr_vars.DefaultFont)

        self.SearchReplace_searchCombo = ttk.Combobox(
            self.toolbar, textvariable=self.SearchReplace_searchVar, justify='center', foreground="purple",
            font=lr_vars.DefaultFont + ' italic')
        self.SearchReplace_replaceCombo = ttk.Combobox(
            self.toolbar, textvariable=self.SearchReplace_replaceVar, justify='center', font=lr_vars.DefaultFont,
            foreground="maroon")

        self.SearchReplace_searchCombo['values'] = ['']
        self.SearchReplace_replaceCombo['values'] = ['']

        self.SearchReplace_button = tk.Button(
            self.toolbar, text='> замена >', font=lr_vars.DefaultFont, command=self._replace_button_set)

    def search_down(self, *a) -> None:
        """поиск вниз, по тексту action.c"""

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
        """поиск вверх, по тексту action.c"""

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
        """поиск в tk_text"""

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
        """перейти на позицию в тексте"""
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
        """поиск в tk_text"""
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
        """менять/вернуть цвет кнопок"""
        if lr_vars.Window._block_:
            try:
                yield
            finally:
                return

        def change() -> None:
            """менять"""
            self.search_entry.config(font='Arial 7 bold')
            self.down_search_button.config(background='orange')
            self.up_search_button.config(background='orange')
            self.search_res_combo.config(font='Arial 7 bold')
            self.update()

        def restore() -> None:
            """вернуть"""
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

    def _replace_button_set(self, *args) -> None:
        """кнопка замены(обычной как в блокноте) текста"""
        if messagebox.askyesno(str(self), "action.c: Заменить ? :\n\n{s}\n\n на :\n\n{r}".format(
                s=self.SearchReplace_searchVar.get(), r=self.SearchReplace_replaceVar.get()), parent=self):
            self.backup()
            text = self.tk_text.get(1.0, tk.END)
            text = text.replace(self.SearchReplace_searchVar.get(), self.SearchReplace_replaceVar.get())
            self.tk_text_to_web_action(text, websReport=True)

