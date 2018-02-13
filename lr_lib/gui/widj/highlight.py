# -*- coding: UTF-8 -*-
# подсветка текста

import string
import itertools
import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.etc.other as lr_other


class HighlightLines:
    '''подсветка линий текста'''
    def __init__(self, tk_text, tegs_names: {str, (str, ), }):
        self.tk_text = tk_text
        self.tegs_names = tegs_names
        self.top_line_num = 1  # on screen line num
        self.bottom_line_num = 1  # on screen line num
        lines = self.tk_text.get(1.0, tk.END).lower().split('\n')
        # неподсвеченные линии текста
        self.on_screen_lines = {num: line.rstrip() for (num, line) in enumerate(lines, start=1) if line.strip()}
        self._max_line = len(lines)  # номер последней линии

    def is_on_screen_lines_change(self, top: int, bottom: int) -> bool:
        '''изменились ли self.top_line_num и self.bottom_line_num'''
        return (self.top_line_num != top) or (self.bottom_line_num != bottom)

    def highlight_line_nums(self, top: int, bottom: int, highlight_cmd=None) -> None:
        '''получать индексы и подсвечивать on-screen линии текста, пока top и bottom не изменились'''
        if self.is_on_screen_lines_change(top, bottom):
            return

        line_nums = (range(top, bottom + 1) & self.on_screen_lines.keys())
        if not line_nums:
            return

        if lr_vars.LineTagAddThread.get():
            tags_highlight = lr_vars.T_POOL_decorator(self.tegs_add)
        else:
            tags_highlight = self.tegs_add
        if lr_vars.TagAddThread.get():
            highlight_cmd = lr_vars.T_POOL_decorator(self.tk_text.tag_add)
        else:
            highlight_cmd = self.tk_text.tag_add

        execute = lr_vars.M_POOL.imap_unordered if lr_vars.HighlightMPool.get() else map
        args = ((num, self.on_screen_lines.get(num), self.tegs_names) for num in line_nums)
        if self.is_on_screen_lines_change(top, bottom):
            return

        for results in execute(search_lines_teg_indxs, lr_other.chunks(args, lr_vars.HighlightLinesPortionSize.get())):
            for line_num, tag_indxs in results:
                if self.is_on_screen_lines_change(top, bottom):
                    return

                tags_highlight(tag_indxs, highlight_cmd)  # подсветить
                self.on_screen_lines.pop(line_num, None)  # больше не подсвечивать
            if self.is_on_screen_lines_change(top, bottom):
                return

    def tegs_add(self, teg_indxs: {str: {(str, str), }, }, highlight_cmd: callable) -> None:
        '''подсветить одну линию, всеми тегами'''
        for teg in teg_indxs:
            for index_start, index_end in teg_indxs[teg]:
                highlight_cmd(teg, index_start, index_end)

    def set_top_bottom(self, top: int, bottom: int) -> None:
        '''новые границы показанных линий'''
        self.top_line_num = top
        self.bottom_line_num = bottom

        if lr_vars.HighlightThread.get():
            highlight_line_nums = lr_vars.T_POOL_decorator(self.highlight_line_nums)
        else:
            highlight_line_nums = self.highlight_line_nums

        highlight_line_nums(top, bottom)


def search_lines_teg_indxs(lines_portion: [(int, str, {str, (str,), }), ]) -> [(int, {str: {(str, str), }}), ]:
    '''вычислить координаты подсветки линии, для порции линий'''
    return tuple(find_tag_indxs(*arg) for arg in lines_portion)


def set_tk_indxs(line_num: int, i_start: int, i_end: int, get_xy='{}.{}'.format) -> (str, str):
    '''индкесы в формате tk.Text'''
    return get_xy(line_num, i_start), get_xy(line_num, i_end + 1)


def join_indxs(indxs: {int, }) -> iter((int, int),):
    '''объединить идущие подряд индексы: {3, 4, 10, 7, 9, 2} -> (2, 4), (7, 7), (9, 10)'''
    index, *indexs = sorted(indxs)
    i_end = i_start = index

    for index in indexs:
        if index != (i_end + 1):
            yield i_start, i_end
            i_start = index
        i_end = index
    else:
        yield i_start, i_end


def find_tag_indxs(line_num: int, line: str, tag_names: {str: {(str, int), }, }) -> (int, {str: [(str, str), ], }):
    '''вычислить координаты подсветки линии'''
    line_indxs = {}

    if line:
        genetate_line_tags_names_indxs(line, line_indxs, tag_names)
        genetate_line_tags_purct_etc_indxs(line, line_indxs)

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


def genetate_line_tags_names_indxs(line: str, line_indxs: dict, teg_names: {str: {(str,int)}}) -> None:
    '''индексы tags для подсветки, для линии - слова из словаря'''
    olive_callback = line_indxs.setdefault(lr_vars.OliveChildTeg, []).extend

    for tag in teg_names:
        teg_callback = line_indxs.setdefault(tag, []).extend
        for name, len_name in teg_names[tag]:
            index = -1

            while True:
                index = line.find(name, index + 1)  # найти
                if index == -1:
                    break

                i = range(index, (index + len_name))
                if any(map(line[index:].startswith, lr_vars.ForceOlive)):
                    olive_callback(i)
                else:
                    teg_callback(i)


punctuation_digits = set(string.punctuation + string.digits).__contains__
whitespace_letters = set(string.whitespace + string.ascii_letters).__contains__


def genetate_line_tags_purct_etc_indxs(line: str, line_indxs: dict) -> None:
    '''индексы подсветки для линии - пунктуация, цифры и не ASCII'''
    punct_digit_callback = line_indxs.setdefault(lr_vars.PunctDigitTag, []).append
    rus_callback = line_indxs.setdefault(lr_vars.RusTag, []).append

    for index, symbol in enumerate(line):
        if whitespace_letters(symbol):
            continue
        elif punctuation_digits(symbol):
            punct_digit_callback(index)
        else:
            rus_callback(index)
