# -*- coding: UTF-8 -*-
# подсветка текста

import string

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.etc.other as lr_other


class HighlightLines:
    """подсветка линий текста"""
    def __init__(self, tk_text, tegs_names: {str, (str, ), }):
        self.tk_text = tk_text

        self.tegs_names = tegs_names

        lines = self.tk_text.get(1.0, tk.END).lower().split('\n')
        self._max_line = len(lines)  # номер последней линии
        self._max_line_proc = (self._max_line / 100)

        # неподсвеченные линии текста
        self.on_screen_lines = {num: line.rstrip() for (num, line) in enumerate(lines, start=1) if line.strip()}
        self.on_srean_line_nums = (0, 0)  # текущие (верхний, нижнй) номера линий, отображенных на экране

        self.highlight_enable = self.tk_text.highlight_var.get()
        self.set_thread_attrs()  # подсвечивать в фоне/главном потоке

        self.HighlightAfter1 = lr_vars.HighlightAfter1
        self.HighlightAfter2 = lr_vars.HighlightAfter2

        # признак необходимости подсветить линии на экране, сама подсветка запускается в lr_vars.MainThreadUpdater
        self.highlight_need = True
        lr_vars.MainThreadUpdater.working = self  # MainThreadUpdater !

    def set_thread_attrs(self) -> None:
        """подсвечивать в фоне/главном потоке"""
        def set() -> None:
            self.highlight_enable = self.tk_text.highlight_var.get()
            self.HighlightAfter1 = int(self.tk_text.action.highlight_After1.get())
            self.HighlightAfter2 = int(self.tk_text.action.highlight_After2.get())
        lr_vars.MainThreadUpdater.submit(set)

    def set_top_bottom(self, on_srean_line_nums: (int, int)) -> None:
        """новые границы показанных линий"""
        self.on_srean_line_nums = on_srean_line_nums
        if self.highlight_enable:  # подсвечивать при вкл
            self.highlight_need = True

    def highlight_top_bottom_lines(self) -> None:
        """подсветить все линии на экране - запускается из MainThreadUpdater"""
        if self.highlight_need:
            self.highlight_need = False  # больше не подсвечивать
            lr_vars.Tk.after(self.HighlightAfter1, self._highlight_top_bottom_lines, self.on_srean_line_nums)

    def _highlight_top_bottom_lines(self, on_srean_line_nums: (int, int)) -> None:
        """подсветить все линии на экране
        получать индексы и подсвечивать on-screen линии текста, пока top и bottom не изменились"""
        if self.on_srean_line_nums != on_srean_line_nums:
            return

        (top, bottom) = on_srean_line_nums
        for line_num in (range(top, (bottom + 1)) & self.on_screen_lines.keys()):
            lr_vars.Tk.after(self.HighlightAfter2, self._line_tegs_add, line_num, on_srean_line_nums)  # подсветить

    def _line_tegs_add(self, line_num: int, on_srean_line_nums: (int, int)) -> None:
        """вычислить координаты подсветки одной линии и подсветить"""
        if self.on_srean_line_nums != on_srean_line_nums:
            return

        line = self.on_screen_lines.pop(line_num, '')  # .pop() - больше не подсвечивать
        if not line:
            return

        line_indxs = {}
        # вычислить
        generate_line_tags_names_indxs(line, line_indxs.setdefault, self.tegs_names)
        genetate_line_tags_purct_etc_indxs(line, line_indxs.setdefault)

        # отфильтровать лишнее
        bg_indxs = set()  # все background
        for teg in line_indxs:
            indxs = set(line_indxs[teg])
            line_indxs[teg] = indxs  # удалить индексы-дубли

            if teg.startswith(lr_vars.ColorMainTegStartswith):
                bg_indxs.update(indxs)

        for teg in line_indxs:  # удалить все background индексы, из не-background тегов
            if not teg.startswith(lr_vars.ColorMainTegStartswith):
                line_indxs[teg] -= bg_indxs

        if lr_vars.OliveChildTeg in line_indxs:  # удалить из Olive тега все индексы, принадлежищие любому другому тегу
            other_tegs = (line_indxs.keys() - lr_vars.minus_teg)
            line_indxs[lr_vars.OliveChildTeg] -= set(i for t in other_tegs for i in line_indxs[t])

        # подсветить
        for teg in line_indxs:
            indxs = line_indxs[teg]
            if indxs:
                for (i_start, i_end) in join_indxs(indxs):
                    self.tk_text.tag_add(teg, '{}.{}'.format(line_num, i_start), '{}.{}'.format(line_num, i_end))


def join_indxs(indxs: {int, }) -> iter((int, int),):
    """объединить идущие подряд индексы, увеличить посл.индекс (+1):
    {3, 10, 4, 7, 9, 2, 1, 11} -> (1, 4(+1)), (7, 7(+1)), (9, 11(+1)) -> (1, 5), (7, 8), (9, 12)"""
    (index, *_indxs) = sorted(indxs)
    i_end = i_start = index

    for index in _indxs:
        i_end += 1

        if index != i_end:
            yield i_start, i_end
            i_start = index

        i_end = index
    else:
        yield i_start, (i_end + 1)


def generate_line_tags_names_indxs(line: str, setdefault: callable, teg_names: {str: {(str, int)}}) -> None:
    """индексы tags для подсветки, для линии - слова из словаря
    teg_names={'backgroundorange': {('warning', 7),..."""
    olive_callback = setdefault(lr_vars.OliveChildTeg, []).extend

    for tag in teg_names:
        teg_callback = setdefault(tag, []).extend
        for (name, len_name) in teg_names[tag]:
            index = -1

            while True:
                index = line.find(name, (index + 1))  # найти
                if index == -1:
                    break

                i = range(index, (index + len_name))
                if any(map(line[index:].startswith, lr_vars.ForceOlive)):
                    olive_callback(i)
                else:
                    teg_callback(i)


punctuation_digits = set(string.punctuation + string.digits)
whitespace_letters = set(string.whitespace + string.ascii_letters)


def genetate_line_tags_purct_etc_indxs(line: str, setdefault: callable) -> None:
    """индексы подсветки для линии - пунктуация, цифры и не ASCII"""
    punct_digit_callback = setdefault(lr_vars.PunctDigitTag, []).append
    rus_callback = setdefault(lr_vars.RusTag, []).append

    for (index, symbol) in enumerate(line):
        if symbol in whitespace_letters:
            continue
        elif symbol in punctuation_digits:
            punct_digit_callback(index)
        else:
            rus_callback(index)
