# -*- coding: UTF-8 -*-
# подсветка текста

import string
import itertools
import threading

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.etc.other as lr_other


# потокобезопасная подсветка одного тега
HTLock = threading.Lock()


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

        # искать индексы в process-пуле или main-потоке
        self.execute = (lr_vars.M_POOL.imap_unordered if lr_vars.HighlightMPool.get() else map)

        def _highlight_cmd(*teg_and_indxs, lock=HTLock) -> None:
            """подсветка одного тега, потокобезопасная - Barrier(1)
            teg_and_indxs=('foregroundolive', '33.3', '33.7')"""
            lock.acquire()
            self.tk_text.tag_add(*teg_and_indxs)
            lock.release()

        # подсветить один тег, в фоне/main-потоке
        self.highlight_cmd = (lr_vars.T_POOL_decorator(_highlight_cmd) if lr_vars.TagAddThread.get() else _highlight_cmd)
        # подсветить одну линию, в фоне/main-потоке
        self.line_tegs_add = (
            lr_vars.T_POOL_decorator(self._line_tegs_add) if lr_vars.LineTagAddThread.get() else self._line_tegs_add)
        # подсветить все линии, в фоне/main-потоке
        self.highlight_top_bottom_lines = (
            lr_vars.T_POOL_decorator(self._highlight_top_bottom_lines) if lr_vars.HighlightThread.get()
            else self._highlight_top_bottom_lines)

    def is_on_screen_lines_change(self, on_srean_line_nums: (int, int)) -> bool:
        """изменились ли self.on_srean_line_nums"""
        return self.on_srean_line_nums != on_srean_line_nums

    def set_top_bottom(self, on_srean_line_nums: (int, int)) -> None:
        """новые границы показанных линий"""
        self.on_srean_line_nums = on_srean_line_nums

        if self.tk_text.highlight_var.get():  # подсветить
            self.highlight_top_bottom_lines(on_srean_line_nums)

    def _highlight_top_bottom_lines(self, on_srean_line_nums: (int, int)) -> None:
        """подсветить все линии на экране"""
        if self.is_on_screen_lines_change(on_srean_line_nums):
            return
        self._highlight_line_nums(on_srean_line_nums)

    def _highlight_line_nums(self, on_srean_line_nums: (int, int)) -> None:
        """получать индексы и подсвечивать on-screen линии текста, пока top и bottom не изменились"""
        (top, bottom) = on_srean_line_nums
        line_nums = (range(top, (bottom + 1)) & self.on_screen_lines.keys())
        if (not line_nums) or self.is_on_screen_lines_change(on_srean_line_nums):
            return

        args = lr_other.chunks(((num, self.on_screen_lines.get(num), self.tegs_names) for num in line_nums), self.psize)
        for ln_ti in self.execute(lines_teg_indxs, args):
            for (line_num, tag_indxs) in ln_ti:
                if self.is_on_screen_lines_change(on_srean_line_nums):
                    return

                self.line_tegs_add(tag_indxs)  # подсветить
                self.on_screen_lines.pop(line_num, None)  # больше не подсвечивать
        
            if self.is_on_screen_lines_change(on_srean_line_nums):
                return

    def _line_tegs_add(self, teg_indxs: {str: {(str, str), }, }) -> None:
        """подсветить одну линию, всеми тегами
        teg_indxs={'foregroundolive': [('40.3', '40.7'),..], 'backgroundblack': [..],..}"""
        for teg in teg_indxs:
            for (index_start, index_end) in teg_indxs[teg]:
                self.highlight_cmd(teg, index_start, index_end)


def lines_teg_indxs(lines_portion: [(int, str, {str, (str,), }), ]) -> [(int, {str: {(str, str), }}), ]:
    """вычислить координаты подсветки линии, для порции линий
    lines_portion=((247, '\t\t"mode=html",', {'backgroundorange': {('*/', 2), ..."""
    return tuple(find_tag_indxs(*arg) for arg in lines_portion)


def set_tk_indxs(line_num: int, i_start: int, i_end: int, get_xy='{}.{}'.format) -> (str, str):
    """индкесы в формате tk.Text"""
    return get_xy(line_num, i_start), get_xy(line_num, i_end + 1)


def join_indxs(indxs: {int, }) -> iter((int, int),):
    """объединить идущие подряд индексы: {3, 4, 10, 7, 9, 2} -> (2, 4), (7, 7), (9, 10)"""
    (index, *indexs) = sorted(indxs)
    i_end = i_start = index

    for index in indexs:
        if index != (i_end + 1):
            yield i_start, i_end
            i_start = index
        i_end = index
    else:
        yield i_start, i_end


def find_tag_indxs(line_num: int, line: str, tag_names: {str: {(str, int), }, }) -> (int, {str: [(str, str), ], }):
    """вычислить координаты подсветки линии
    teg_names={'backgroundorange': {('warning', 7),..."""
    line_indxs = {}

    if line:
        setdefault = line_indxs.setdefault
        generate_line_tags_names_indxs(line, setdefault, tag_names)
        genetate_line_tags_purct_etc_indxs(line, setdefault)

        bg_indxs = set()
        for teg in line_indxs:
            indxs = set(line_indxs[teg])
            line_indxs[teg] = indxs
            if teg.startswith(lr_vars.ColorMainTegStartswith):
                bg_indxs.update(indxs)

        for teg in line_indxs:
            if not teg.startswith(lr_vars.ColorMainTegStartswith):
                line_indxs[teg] -= bg_indxs

        if lr_vars.OliveChildTeg in line_indxs:
            other_tegs = (line_indxs.keys() - lr_vars.minus_teg)
            line_indxs[lr_vars.OliveChildTeg] -= set(itertools.chain(*map(line_indxs.__getitem__, other_tegs)))

        line_indxs = {k: [set_tk_indxs(line_num, i_start, i_end) for (i_start, i_end) in join_indxs(indxs)]
                      for (k, indxs) in line_indxs.items() if indxs}

    return line_num, line_indxs


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
