# -*- coding: UTF-8 -*-
# подсветка текста

import string

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars as lr_vars


class HighlightLines:
    """подсветка линий текста"""
    def __init__(self, tk_text: 'lr_lib.gui.widj.highlight_text.HighlightText', tegs_names: {str, (str, ), }):
        self.tk_text = tk_text
        self.id = id(self)

        self.tegs_names = tegs_names

        lines = self.tk_text.get(1.0, tk.END).lower().split('\n')
        self._max_line = len(lines)  # номер последней линии
        self._max_line_proc = (self._max_line / 100)

        # неподсвеченные линии текста
        self.on_screen_lines = {num: line.rstrip() for (num, line) in enumerate(lines, start=1) if line.strip()}
        self.on_sreen_line_nums = (0, 0)  # текущие (верхний, нижнй) номера линий, отображенных на экране

        self.highlight_enable = self.tk_text.highlight_var.get()
        self.set_thread_attrs()

        self.HighlightAfter0 = lr_vars.HighlightAfter0
        self.HighlightAfter1 = lr_vars.HighlightAfter1
        self.HighlightAfter2 = lr_vars.HighlightAfter2

        # признак необходимости подсветить линии на экране
        self.highlight_need = True
        self.after = self.tk_text.after
        return

    def set_thread_attrs(self) -> None:
        """взять настройки подсветки, из виджетов"""
        def set() -> None:
            """lr_vars.MainThreadUpdater.submit(set)"""
            self.highlight_enable = self.tk_text.highlight_var.get()
            self.HighlightAfter0 = int(self.tk_text.action.highlight_After0.get())
            self.HighlightAfter1 = int(self.tk_text.action.highlight_After1.get())
            self.HighlightAfter2 = int(self.tk_text.action.highlight_After2.get())
            return

        lr_vars.MainThreadUpdater.submit(set)
        return

    def set_top_bottom(self, on_sreen_line_nums: (int, int), __highlight=True) -> None:
        """новые границы показанных линий"""
        self.on_sreen_line_nums = on_sreen_line_nums
        if self.highlight_enable:  # подсвечивать при вкл
            self.highlight_need = __highlight
        return

    def highlight_callback(self, __highlight=False) -> None:
        """подсветить все линии на экране"""
        if self.highlight_need:
            self.highlight_need = __highlight
            # подсветить
            self.after(self.HighlightAfter1, self.highlight_top_bottom_lines, self.on_sreen_line_nums)
        return

    def highlight_top_bottom_lines(self, on_sreen_line_nums: (int, int)) -> None:
        """подсветить все линии на экране
        получать индексы и подсвечивать on-screen линии текста, пока top и bottom не изменились"""
        if self.on_sreen_line_nums != on_sreen_line_nums:
            return

        (top, bottom) = on_sreen_line_nums
        for line_num in (range(top, (bottom + 1)) & self.on_screen_lines.keys()):
            self.after(self.HighlightAfter2, self._line_tegs_add, line_num, on_sreen_line_nums)  # подсветить
            continue
        return

    def _line_tegs_add(self, line_num: int, on_sreen_line_nums: (int, int), XY='{}.{}'.format) -> None:
        """вычислить координаты подсветки одной линии и подсветить"""
        if self.on_sreen_line_nums != on_sreen_line_nums:
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
            continue

        for teg in line_indxs:  # удалить все background индексы, из не-background тегов
            if not teg.startswith(lr_vars.ColorMainTegStartswith):
                line_indxs[teg] -= bg_indxs
            continue

        if lr_vars.OliveChildTeg in line_indxs:  # удалить из Olive тега все индексы, принадлежищие любому другому тегу
            other_tegs = (line_indxs.keys() - lr_vars.minus_teg)
            line_indxs[lr_vars.OliveChildTeg] -= set(i for t in other_tegs for i in line_indxs[t])

        # подсветить
        tag_add = self.tk_text.tag_add
        for teg in line_indxs:
            indxs = line_indxs[teg]
            if indxs:
                for (i_start, i_end) in join_indxs(*sorted(indxs)):
                    tag_add(teg, XY(line_num, i_start), XY(line_num, i_end))
                    continue
            continue
        return


def join_indxs(index: int, *indxs: sorted) -> iter((int, int),):
    """ join_indxs(*sorted(indxs))
    объединить идущие подряд индексы, увеличить посл.индекс (+1):
     indxs = {1, 2, 3, 4, 7, 9, 10, 11} -> (1, 4(+1)), (7, 7(+1)), (9, 11(+1)) -> (1, 5), (7, 8), (9, 12)"""
    i_end = i_start = index

    for index in indxs:
        i_end += 1

        if index != i_end:
            yield i_start, i_end
            i_start = index

        i_end = index
        continue
    else:
        yield i_start, (i_end + 1)
    return


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
                continue
            continue
        continue
    return


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
        continue
    return
