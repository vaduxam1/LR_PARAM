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

        self.psize = lr_vars.HighlightLinesPortionSize.get()
        self.tegs_names = tegs_names

        lines = self.tk_text.get(1.0, tk.END).lower().split('\n')
        self._max_line = len(lines)  # номер последней линии
        self._max_line_proc = (self._max_line / 100)

        # неподсвеченные линии текста
        self.on_screen_lines = {num: line.rstrip() for (num, line) in enumerate(lines, start=1) if line.strip()}
        self.on_srean_line_nums = (0, 0)  # текущие (верхний, нижнй) номера линий, отображенных на экране

        self.highlight_enable = self.tk_text.highlight_var.get()
        self.execute = (lr_vars.M_POOL.imap_unordered if lr_vars.HighlightMPool.get() else map)  # искать индексы в process-пуле или main-потоке
        self.set_thread_attrs()  # подсвечивать в фоне/главном потоке

        self.HighlightAfter1 = lr_vars.HighlightAfter1
        self.HighlightAfter2 = lr_vars.HighlightAfter2

    def set_thread_attrs(self) -> None:
        """подсвечивать в фоне/главном потоке"""
        def set() -> None:
            self.psize = lr_vars.HighlightLinesPortionSize.get()
            self.highlight_enable = self.tk_text.highlight_var.get()
            self.execute = (lr_vars.M_POOL.imap_unordered if lr_vars.HighlightMPool.get() else map)
            self.HighlightAfter1 = int(self.tk_text.action.highlight_After1.get())
            self.HighlightAfter2 = int(self.tk_text.action.highlight_After2.get())

        lr_vars.MainThreadUpdater.submit(set)

    def set_top_bottom(self, on_srean_line_nums: (int, int)) -> None:
        """новые границы показанных линий"""
        self.on_srean_line_nums = on_srean_line_nums

        if self.highlight_enable:  # подсветить
            lr_vars.Tk.after(self.HighlightAfter1, self._highlight_top_bottom_lines, on_srean_line_nums)

    def _highlight_top_bottom_lines(self, on_srean_line_nums: (int, int)) -> None:
        """подсветить все линии на экране
        получать индексы и подсвечивать on-screen линии текста, пока top и bottom не изменились"""
        if self.on_srean_line_nums != on_srean_line_nums:
            return

        (top, bottom) = on_srean_line_nums
        line_nums = (range(top, (bottom + 1)) & self.on_screen_lines.keys())
        if (not line_nums) or (self.on_srean_line_nums != on_srean_line_nums):
            return

        args = lr_other.chunks(((num, self.on_screen_lines.get(num), self.tegs_names) for num in line_nums), self.psize)
        for results in self.execute(lines_teg_indxs, args):
            for (line_num, tag_indxs) in results:
                if self.on_srean_line_nums != on_srean_line_nums:
                    return

                # подсветить
                lr_vars.Tk.after(self.HighlightAfter2, self._line_tegs_add, tag_indxs, line_num)

            if self.on_srean_line_nums != on_srean_line_nums:
                return

    def _line_tegs_add(self, teg_indxs: {str: {(str, str), }, }, line_num: int) -> None:
        """подсветить одну линию, всеми тегами
        teg_indxs={'foregroundolive': [('40.3', '40.7'),..], 'backgroundblack': [..],..}"""
        for teg in teg_indxs:
            for (index_start, index_end) in teg_indxs[teg]:
                self.tk_text.tag_add(teg, index_start, index_end)
        self.on_screen_lines.pop(line_num, None)  # больше не подсвечивать


def lines_teg_indxs(lines_portion: [(int, str, {str, (str,), }), ]) -> [(int, {str: {(str, str), }}), ]:
    """вычислить координаты подсветки линии, для порции линий
    lines_portion=((247, '\t\t"mode=html",', {'backgroundorange': {('*/', 2), ..."""
    return tuple(map(find_tag_indxs, lines_portion))


def find_tag_indxs(arg: (int, str, {str, (str,), })) -> (int, {str: [(str, str), ], }):
    """вычислить координаты подсветки линии
    arg=(19, '\t\t"url=zkau/delete.png", enditem,', {'backgroundorange': {('yandex.ru',..."""
    (line_num, line, tag_names) = arg

    line_indxs = {}
    if line:
        setdefault = line_indxs.setdefault
        generate_line_tags_names_indxs(line, setdefault, tag_names)
        genetate_line_tags_purct_etc_indxs(line, setdefault)
        line_indxs = filter_tag_indxs(line_num, line_indxs)

    return line_num, line_indxs


def filter_tag_indxs(line_num: int, line_indxs: dict) -> dict:
    """привести, вычисленные индексы текста, в нужный формат"""
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

    line_indxs = {k: [set_tk_indxs(line_num, i_start, i_end) for (i_start, i_end) in join_indxs(indxs)]
                  for (k, indxs) in line_indxs.items() if indxs}

    return line_indxs


def set_tk_indxs(line_num: int, i_start: int, i_end: int) -> (str, str):
    """индкесы в формате tk.Text"""
    return '{}.{}'.format(line_num, i_start), '{}.{}'.format(line_num, i_end)


def join_indxs(indxs: {int, }) -> iter((int, int),):
    """объединить идущие подряд индексы: {3, 10, 4, 7, 9, 2, 1, 11} -> (1, 4), (7, 7), (9, 11)"""
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
