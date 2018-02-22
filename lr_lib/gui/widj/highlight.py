# -*- coding: UTF-8 -*-
# подсветка текста

import string
import itertools
import threading

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.etc.other as lr_other

# thread safe
HighlightThreadBarrier = threading.Barrier(1)


class HighlightLines:
    """подсветка линий текста"""
    def __init__(self, tk_text, tegs_names: {str, (str, ), }):
        self.tk_text = tk_text

        self.tegs_names = tegs_names
        self.on_srean_line_nums = (0, 0)  # on screen line nums

        lines = self.tk_text.get(1.0, tk.END).lower().split('\n')
        # неподсвеченные линии текста
        self.on_screen_lines = {num: line.rstrip() for (num, line) in enumerate(lines, start=1) if line.strip()}
        self._max_line = len(lines)  # номер последней линии
        self._max_line_proc = (self._max_line / 100)

        def tag_apply(*a, **kw) -> None:
            """команда подсветки"""
            HighlightThreadBarrier.wait()
            self.tk_text.tag_add(*a, **kw)

        if lr_vars.TagAddThread.get():
            self.highlight_cmd = lr_vars.T_POOL_decorator(tag_apply)
        else:
            self.highlight_cmd = tag_apply

        if lr_vars.LineTagAddThread.get():
            self.tags_highlight = lr_vars.T_POOL_decorator(tegs_add)
        else:
            self.tags_highlight = tegs_add

        if lr_vars.HighlightThread.get():
            self.highlight_lines = lr_vars.T_POOL_decorator(self._highlight_top_bottom_lines)
        else:
            self.highlight_lines = self._highlight_top_bottom_lines

        self.execute = lr_vars.M_POOL.imap_unordered if lr_vars.HighlightMPool.get() else map
        self.psize = lr_vars.HighlightLinesPortionSize.get()

    def is_on_screen_lines_change(self, on_srean_line_nums: (int, int)) -> bool:
        """изменились ли self.on_srean_line_nums"""
        return self.on_srean_line_nums != on_srean_line_nums

    def set_top_bottom(self, on_srean_line_nums: (int, int)) -> None:
        """новые границы показанных линий"""
        self.on_srean_line_nums = on_srean_line_nums

        if self.tk_text.highlight_var.get():  # подсветить
            self._highlight_top_bottom_lines(on_srean_line_nums)

    def _highlight_top_bottom_lines(self, on_srean_line_nums: (int, int)) -> None:
        """подсветить линии на экране"""
        if self.is_on_screen_lines_change(on_srean_line_nums):
            return
        self._highlight_line_nums(on_srean_line_nums)

    def _highlight_line_nums(self, on_srean_line_nums: (int, int)) -> None:
        """получать индексы и подсвечивать on-screen линии текста, пока top и bottom не изменились"""
        top, bottom = on_srean_line_nums
        line_nums = (range(top, (bottom + 1)) & self.on_screen_lines.keys())
        if (not line_nums) or self.is_on_screen_lines_change(on_srean_line_nums):
            return

        args = lr_other.chunks(((num, self.on_screen_lines.get(num), self.tegs_names) for num in line_nums), self.psize)
        for ln_ti in self.execute(lines_teg_indxs, args):
            for (line_num, tag_indxs) in ln_ti:
                if self.is_on_screen_lines_change(on_srean_line_nums):
                    return

                self.tags_highlight(tag_indxs, self.highlight_cmd)  # подсветить
                self.on_screen_lines.pop(line_num, None)  # больше не подсвечивать
        
            if self.is_on_screen_lines_change(on_srean_line_nums):
                return


def tegs_add(teg_indxs: {str: {(str, str), }, }, highlight_cmd: callable) -> None:
    """подсветить одну линию, всеми тегами"""
    for teg in teg_indxs:
        for (index_start, index_end) in teg_indxs[teg]:
            highlight_cmd(teg, index_start, index_end)


def lines_teg_indxs(lines_portion: [(int, str, {str, (str,), }), ]) -> [(int, {str: {(str, str), }}), ]:
    """вычислить координаты подсветки линии, для порции линий"""
    return tuple(find_tag_indxs(*arg) for arg in lines_portion)


def set_tk_indxs(line_num: int, i_start: int, i_end: int, get_xy='{}.{}'.format) -> (str, str):
    """индкесы в формате tk.Text"""
    return get_xy(line_num, i_start), get_xy(line_num, i_end + 1)


def join_indxs(indxs: {int, }) -> iter((int, int),):
    """объединить идущие подряд индексы: {3, 4, 10, 7, 9, 2} -> (2, 4), (7, 7), (9, 10)"""
    index, *indexs = sorted(indxs)
    i_end = i_start = index

    for index in indexs:
        if index != (i_end + 1):
            yield i_start, i_end
            i_start = index
        i_end = index
    else:
        yield i_start, i_end


ColorMainTegStartswith = lr_vars.ColorMainTegStartswith
OliveChildTeg = lr_vars.OliveChildTeg
minus_teg = lr_vars.minus_teg


def find_tag_indxs(line_num: int, line: str, tag_names: {str: {(str, int), }, }) -> (int, {str: [(str, str), ], }):
    """вычислить координаты подсветки линии"""
    line_indxs = {}

    if line:
        setdefault = line_indxs.setdefault
        genetate_line_tags_names_indxs(line, setdefault, tag_names)
        genetate_line_tags_purct_etc_indxs(line, setdefault)

        bg_indxs = set()
        bg_update = bg_indxs.update
        for teg in line_indxs:
            indxs = set(line_indxs[teg])
            line_indxs[teg] = indxs
            if teg.startswith(ColorMainTegStartswith):
                bg_update(indxs)

        for teg in line_indxs:
            if not teg.startswith(ColorMainTegStartswith):
                line_indxs[teg] -= bg_indxs

        if OliveChildTeg in line_indxs:
            other_tegs = (line_indxs.keys() - minus_teg)
            line_indxs[OliveChildTeg] -= set(itertools.chain(*map(line_indxs.__getitem__, other_tegs)))

        line_indxs = {k: [set_tk_indxs(line_num, i_start, i_end) for (i_start, i_end) in join_indxs(indxs)]
                      for (k, indxs) in line_indxs.items() if indxs}

    return line_num, line_indxs


ForceOlive = lr_vars.ForceOlive


def genetate_line_tags_names_indxs(line: str, setdefault: callable, teg_names: {str: {(str,int)}}) -> None:
    """индексы tags для подсветки, для линии - слова из словаря"""
    olive_callback = setdefault(OliveChildTeg, []).extend
    find = line.find

    for tag in teg_names:
        teg_callback = setdefault(tag, []).extend
        for (name, len_name) in teg_names[tag]:
            index = -1

            while True:
                index = find(name, (index + 1))  # найти
                if index == -1:
                    break

                i = range(index, (index + len_name))
                if any(map(line[index:].startswith, ForceOlive)):
                    olive_callback(i)
                else:
                    teg_callback(i)


punctuation_digits = set(string.punctuation + string.digits)
whitespace_letters = set(string.whitespace + string.ascii_letters)
RusTag = lr_vars.RusTag
PunctDigitTag = lr_vars.PunctDigitTag


def genetate_line_tags_purct_etc_indxs(line: str, setdefault: callable) -> None:
    """индексы подсветки для линии - пунктуация, цифры и не ASCII"""
    punct_digit_callback = setdefault(PunctDigitTag, []).append
    rus_callback = setdefault(RusTag, []).append

    for (index, symbol) in enumerate(line):
        if symbol in whitespace_letters:
            continue
        elif symbol in punctuation_digits:
            punct_digit_callback(index)
        else:
            rus_callback(index)
