# -*- coding: UTF-8 -*-
# gui виджет цветного текста с номерами линий

import re
import copy
import string
import itertools
import tkinter as tk
from tkinter.font import Font

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.etc.other as lr_other


def set_word_boundaries(root) -> None:
    '''
    ограничить область выделения(в tk.Text)
    '''
    # this first statement triggers tcl to autoload the library
    # that defines the variables we want to override.
    root.tk.call('tcl_wordBreakAfter', '', 0)

    # this defines what tcl considers to be a "word". For more
    # information see http://www.tcl.tk/man/tcl8.5/TclCmd/library.htm#M19
    root.tk.call('set', 'tcl_wordchars', '[a-zA-Z0-9_.!-]')
    root.tk.call('set', 'tcl_nonwordchars', '[^a-zA-Z0-9_.!-]')


class HighlightLines:
    '''подсветка линий текста'''
    def __init__(self, tk_text, tegs_names: {str, (str, ), }):
        self.tk_text = tk_text
        self.tegs_names = tegs_names
        self.top_line_num = 1  # on screen line num
        self.bottom_line_num = 1  # on screen line num
        lines = self.tk_text.get(1.0, tk.END).lower().split('\n')
        self._max_line = len(lines)  # номер последней линии
        # неподсвеченные линии текста
        self.on_screen_lines = {num: line.rstrip() for num, line in enumerate(lines, start=1) if line.strip()}

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
    '''объединить идущие подряд индексы: (3, 4, 10, 7, 9, 2, 10) -> (2, 4), (7, 7), (9, 10)'''
    index, *indexs = sorted(indxs)
    i_end = i_start = index

    for index in indexs:
        if index != (i_end + 1):
            yield i_start, i_end
            i_start = index
        i_end = index
    else:
        yield i_start, i_end


_NC = 'foregroundolive'  # не подсветит этим тегом, если подсвечено любым другим
_BG = 'background'  # не подсветит другим тегом, если подсвечено этим


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
            if teg.startswith(_BG):
                bg_indxs.update(indxs)

        for teg in line_indxs:
            if not teg.startswith(_BG):
                line_indxs[teg] -= bg_indxs

        if _NC in line_indxs:
            line_indxs[_NC] -= set(itertools.chain(*map(line_indxs.__getitem__, (line_indxs.keys() - {_NC}))))

        line_indxs = {k: [set_tk_indxs(line_num, i_start, i_end) for (i_start, i_end) in join_indxs(indxs)]
                      for (k, indxs) in line_indxs.items() if indxs}

    return line_num, line_indxs


def genetate_line_tags_names_indxs(line: str, line_indxs: dict, teg_names: {str: {(str,int)}}) -> None:
    '''индексы tags для подсветки, для линии - слова из словаря'''
    olive_callback = line_indxs.setdefault('foregroundolive', []).extend

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


class HighlightText(tk.Text):
    '''tk.Text'''
    def __init__(self, *args, **kwargs):
        self.action = args[0]
        bind = kwargs.pop('bind', None)
        super().__init__(*args, **kwargs)

        self.highlight_dict = copy.deepcopy(lr_vars.VarDefaultColorTeg)
        self.highlight_lines = HighlightLines(self, self.get_tegs_names())

        set_word_boundaries(self)  # ограничить область выделения(в tk.Text)

        self.font_var = tk.StringVar(value=kwargs.get('font_var', lr_vars.DefaultActionNoHighlightFont))
        self.size_var = tk.IntVar(value=kwargs.get('size_var', lr_vars.DefaultActionNoHighlightFontSize))
        self.weight_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontBold)
        self.underline_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontUnderline)
        self.slant_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontSlant)
        self.overstrike_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontOverstrike)
        self.highlight_var = tk.BooleanVar(value=lr_vars.HighlightOn)

        self.set_tegs()

        self.tk.eval('''
                    proc widget_proxy {widget widget_command args} {

                        # call the real tk widget command with the real args
                        set result [uplevel [linsert $args 0 $widget_command]]

                        # generate the event for certain types of commands
                        if {([lindex $args 0] in {insert replace delete}) ||
                            ([lrange $args 0 2] == {mark set insert}) || 
                            ([lrange $args 0 1] == {xview moveto}) ||
                            ([lrange $args 0 1] == {xview scroll}) ||
                            ([lrange $args 0 1] == {yview moveto}) ||
                            ([lrange $args 0 1] == {yview scroll})} {

                            event generate  $widget <<Change>> -when tail
                        }

                        # return the result from the real widget command
                        return $result
                    }
                    ''')
        self.tk.eval('''
                    rename {widget} _{widget}
                    interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
                '''.format(widget=str(self)))

        if bind:
            self.bind("<<Change>>", self._on_change)
            self.bind("<Configure>", self._on_change)

        self.linenumbers = TextLineNumbers(self)

        self.bind_all("<Control-z>", self.undo)
        self.bind_all("<Control-y>", self.redo)

    def undo(self, event):
        return self.edit_undo()

    def redo(self, event):
        return self.edit_redo()

    def _on_change(self, event=None):
        self.linenumbers.redraw()

    def new_text_set(self, text: str) -> None:
        '''заменить весь текст на новый'''
        self.delete(1.0, tk.END)
        self.insert(1.0, text)

    def _text_checkbox(self) -> (str, str, int, int):
        '''text checkbox's get'''
        w = 'bold' if self.weight_var.get() else 'normal'
        s = 'italic' if self.slant_var.get() else 'roman'
        u = 1 if self.underline_var.get() else 0
        o = 1 if self.overstrike_var.get() else 0
        return w, s, u, o,

    def set_tegs(self, *a, remove=False, parent=None, ground=('background', 'foreground',)) -> None:
        '''создать/удалить теги, для parent/self'''
        if remove:
            for tag in self.tag_names():
                if any(tag.startswith(g) for g in ground):
                    self.tag_delete(tag)
            return

        if parent is None:
            parent = self

        tegs = lr_vars.VarColorTeg.get()
        w, s, u, o = self.__class__._text_checkbox(parent)
        f = Font(family=parent.font_var.get(), size=parent.size_var.get(), weight=w, slant=s, underline=u, overstrike=o)

        for g in ground:
            for color in tegs:
                self.tag_config(g + color, **{g: color, 'font': f, })

    def reset_highlight(self, highlight=True) -> None:
        '''сбросить текст настройки цветов'''
        self.highlight_dict.clear()
        self.highlight_dict.update(copy.deepcopy(lr_vars.VarDefaultColorTeg))
        if highlight:
            self.set_highlight()

    def set_font(self, *a, size=None) -> None:
        if size is None:
            size = self.size_var.get()
        w, s, u, o = self._text_checkbox()
        self.configure(font=Font(family=self.font_var.get(), size=size, weight=w, slant=s, underline=u, overstrike=o))

    def set_highlight(self) -> None:
        '''tk.Text tag_add/remove, сформировать on_screen_lines "карту" подсветки'''
        self.set_tegs(remove=True)

        if self.highlight_var.get():
            self.set_tegs(remove=False, parent=self)
            self.set_tegs(remove=False, parent=self.action)
            self.highlight_lines = HighlightLines(self, self.get_tegs_names())
            self.action.report_position()  # показать

    def get_tegs_names(self) -> {str: {str,}}:
        '''_tegs_names'''
        tegs_names = {}
        hex_unicode_words = re.compile('\\\\x\w\w').findall(self.get(1.0, tk.END))  # \\xCE\\xE1
        self.highlight_dict.setdefault('foreground', dict()).setdefault('olive', set()).update(hex_unicode_words)

        for ground in self.highlight_dict:
            colors = self.highlight_dict[ground]
            for color in colors:
                tag = ground + color
                for name in colors[color]:

                    task = (name.lower(), len(name))
                    try:
                        tegs_names[tag].add(task)
                    except (KeyError, AttributeError):
                        tegs_names[tag] = {task}

        return tegs_names


class TextLineNumbers(tk.Canvas):
    '''номера линий tk.Text'''
    def __init__(self, parent_: HighlightText):
        super().__init__(parent_.action, background=lr_vars.Background)
        self.textwidget = parent_
        self.linenum = -1

    def redraw(self, *args, __restart=False) -> None:
        '''redraw line numbers'''
        self.delete("all")
        i = self.textwidget.index("@0,0")
        self.linenum = 0

        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break

            y = dline[1]
            self.linenum = str(i).split(".", 1)[0]
            self.create_text(2, y, anchor="nw", text=self.linenum)
            i = self.textwidget.index("%s+1line" % i)

        self.textwidget.action.scroll_lab.config(text=self.textwidget.highlight_lines._max_line)
