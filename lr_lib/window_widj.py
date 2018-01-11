# -*- coding: UTF-8 -*-
# gui виджеты

import re
import copy
import string
import itertools
import contextlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font

from lr_lib import (
    defaults,
    other as lr_other,
    pool as lr_pool,
    logger as lr_log,
)

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

        line_nums = range(top, bottom + 1) & self.on_screen_lines.keys()
        if not line_nums:
            return

        if defaults.LineTagAddThread.get():
            tags_highlight = lr_pool.T_POOL_execute_decotator(self.tegs_add)
        else:
            tags_highlight = self.tegs_add
        if defaults.TagAddThread.get():
            highlight_cmd = lr_pool.T_POOL_execute_decotator(self.tk_text.tag_add)
        else:
            highlight_cmd = self.tk_text.tag_add

        execute = lr_pool.M_POOL.imap_unordered if defaults.HighlightMPool.get() else map
        args = ((num, self.on_screen_lines.get(num), self.tegs_names) for num in line_nums)
        if self.is_on_screen_lines_change(top, bottom):
            return

        for results in execute(search_lines_teg_indxs, lr_other.chunks(args, defaults.HighlightLinesPortionSize.get())):
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

        if defaults.HighlightThread.get():
            highlight_line_nums = lr_pool.T_POOL_execute_decotator(self.highlight_line_nums)
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
                if any(map(line[index:].startswith, defaults.ForceOlive)):
                    olive_callback(i)
                else:
                    teg_callback(i)


punctuation_digits = set(string.punctuation + string.digits).__contains__
whitespace_letters = set(string.whitespace + string.ascii_letters).__contains__


def genetate_line_tags_purct_etc_indxs(line: str, line_indxs: dict) -> None:
    '''индексы подсветки для линии - пунктуация, цифры и не ASCII'''
    punct_digit_callback = line_indxs.setdefault(defaults.PunctDigitTag, []).append
    rus_callback = line_indxs.setdefault(defaults.RusTag, []).append

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

        self.highlight_dict = copy.deepcopy(defaults.VarDefaultColorTeg)
        self.highlight_lines = HighlightLines(self, self.get_tegs_names())

        set_word_boundaries(self)  # ограничить область выделения(в tk.Text)

        self.font_var = tk.StringVar(value=kwargs.get('font_var', defaults.DefaultActionNoHighlightFont))
        self.size_var = tk.IntVar(value=kwargs.get('size_var', defaults.DefaultActionNoHighlightFontSize))
        self.weight_var = tk.BooleanVar(value=defaults.DefaultActionNoHighlightFontBold)
        self.underline_var = tk.BooleanVar(value=defaults.DefaultActionNoHighlightFontUnderline)
        self.slant_var = tk.BooleanVar(value=defaults.DefaultActionNoHighlightFontSlant)
        self.overstrike_var = tk.BooleanVar(value=defaults.DefaultActionNoHighlightFontOverstrike)
        self.highlight_var = tk.BooleanVar(value=defaults.HighlightOn)

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
        self.linenumbers.attach(self)

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

        tegs = defaults.VarColorTeg.get()
        w, s, u, o = self.__class__._text_checkbox(parent)
        f = Font(family=parent.font_var.get(), size=parent.size_var.get(), weight=w, slant=s, underline=u, overstrike=o)

        for g in ground:
            for color in tegs:
                self.tag_config(g + color, **{g: color, 'font': f, })

    def reset_highlight(self, highlight=True) -> None:
        '''сбросить текст настройки цветов'''
        self.highlight_dict.clear()
        self.highlight_dict.update(copy.deepcopy(defaults.VarDefaultColorTeg))
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
        super().__init__(parent_.action, background=defaults.Background)
        self.parent_ = parent_
        self.textwidget = None
        self.linenum = -1

    def attach(self, text_widget) -> None:
        self.textwidget = text_widget

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

        self.parent_.action.scroll_lab.config(text=self.textwidget.highlight_lines._max_line)


class WebLegend(tk.Toplevel):
    '''окно web_ леленды'''
    def __init__(self, parent):
        super().__init__(master=parent, padx=0, pady=0)
        self.geometry('{}x{}'.format(*defaults._Tk_LegendWIND_SIZE))
        self.web_canavs = {}

        self.parent = parent
        self.minimal_canvas_size = list(defaults.Legend_minimal_canvas_size)
        self.H = tk.IntVar(value=defaults.LegendHight)

        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)

        hscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)

        self.canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.config(scrollregion='0 0 %s %s' % tuple(self.minimal_canvas_size))

        self.interior = tk.Frame(self.canvas)
        # interior_id = self.canvas.create_window(0, 0, window=interior, anchor=tk.NW)
        self.interior.bind('<Configure>', self._configure_interior)

        self.h_entry = tk.Spinbox(
            self, width=4, justify='center', from_=0, to=9999, command=lambda *a: self.print(transac_show=False),
            textvariable=self.H)
        self.h_entry.pack()

    def _configure_interior(self, *args) -> None:
        '''update the scrollbars to match the size of the inner frame'''
        size = (max(self.interior.winfo_reqwidth(), self.minimal_canvas_size[0]),
                max(self.interior.winfo_reqheight(), self.minimal_canvas_size[1]))
        self.canvas.config(scrollregion='0 0 %s %s' % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def add_web_canavs(self):
        for web_ in self.parent.web_action.get_web_snapshot_all():
            self.web_canavs[web_.snapshot] = {1: {}, 2: {}, 'enable': True, 'enable_in': True}

    def print(self, transac_show=True) -> None:
        colors = iter(itertools.cycle(defaults.VarColorTeg.get() - {'white', 'black', 'navy', }))
        self.canvas.delete("all")
        web_actions = tuple(self.parent.web_action.get_web_snapshot_all())
        sep = 25
        w_ = 30
        width = 40
        height = 35
        wdt = {w.snapshot: w for w in web_actions}
        self.minimal_canvas_size[0] = defaults.Legend_scroll_len_modificator * len(wdt)
        self._configure_interior()
        _transaction = None
        tr = []
        lt = 0
        H = self.H.get()
        lcolor = 'black'

        for i in self.web_canavs:
            transaction = wdt[i].transaction

            if transaction != _transaction:
                if transaction:
                    lt = len(tr)
                    lcolor = color = next(colors)
                else:
                    lt = None
                    lcolor = color = 'white'
                t = (lt, transaction)
                text = '({})->'.format(lt)
                tr.append(t)
            else:
                text = '<-{}'.format(lt)

            self.canvas.create_text((sep + 40), 10, text=text)
            if color in ('white', 'yellow', ):
                lcolor = 'black'

            xy1 = lcolor, sep, 20, (width + sep + w_), (20 + height)

            def onObjectClick1(event, i=i) -> None:
                '''показать/удалить линии out'''
                self.canvas.delete("all")
                self.web_canavs[i]['enable'] = not self.web_canavs[i]['enable']
                self.print(transac_show=False)

            def onObjectClick2(event, i=i) -> None:
                '''показать/удалить линии in'''
                self.canvas.delete("all")
                self.web_canavs[i]['enable_in'] = not self.web_canavs[i]['enable_in']
                self.print(transac_show=False)

            if wdt[i].web_reg_save_param_list:
                shape_1 = self.canvas.create_rectangle(*xy1[1:], fill=color, width=2)

                self.canvas.tag_bind(shape_1, '<ButtonPress-1>', onObjectClick1)
            self.web_canavs[i][1] = list(xy1)

            t1 = self.canvas.create_text(
                sep + w_, 35, text='Snap: {}\nout: {}'.format(i, len(wdt[i].web_reg_save_param_list)))

            self.canvas.tag_bind(t1, '<ButtonPress-1>', onObjectClick1)
            if transaction != _transaction:
                self.canvas.create_text((sep + w_), (H + 45), text='transac({})'.format(lt if transaction else "''"))
                _transaction = transaction

            xy2 = sep, H, (width + sep + w_), (H + height)
            shape_2 = self.canvas.create_rectangle(*xy2, fill=color, width=2)
            self.canvas.tag_bind(shape_2, '<ButtonPress-1>', onObjectClick2)
            self.web_canavs[i][2] = list(xy2)

            t2 = self.canvas.create_text(
                (sep + w_), (H + 15), text='in: {1}\nSnap: {0}'.format(i, ''))  # wdt[i].param_in_web_report()[1]
            self.canvas.tag_bind(t2, '<ButtonPress-1>', onObjectClick2)

            sep += 70

        rep = self.parent.web_action.websReport.param_statistic

        x = 20
        for web_ in web_actions:
            if self.web_canavs[web_.snapshot]['enable']:
                color, *xy1 = self.web_canavs[web_.snapshot][1]

                for w in web_.web_reg_save_param_list:
                    dt = rep[w.name]

                    for i in dt['snapshots']:
                        if self.web_canavs[i]['enable_in']:
                            xy2 = self.web_canavs[i][2]
                            l = self.canvas.create_line(xy1[2]-x, xy1[3], xy2[0]+x, xy2[1], fill=color, arrow=tk.LAST, width=2)

                            def title(*a, w=w, web_=web_, dt=dt, rep=rep, i=i) -> None:
                                '''описание param в title'''
                                self.title(
                                    'OUT(t{oi}.snapshot): {p} | {n} | count(in_webs={c}, webs={wwp}, '
                                    'transac_={twp}, infs={il}  ||  IN(t{i}.snapshot): {rep}'.format(
                                        p=w.param, n=w.name, c=dt['param_count'], wwp=dt['snapshots'],
                                        twp=dt['transaction_count'], il=len(dt['snapshots']), rep=rep[i], oi=web_.snapshot, i=i))

                            self.canvas.tag_bind(l, '<ButtonPress-1>', title)

        if transac_show:
            t = [(a, b) for (a, b) in tr if b]
            if t:
                tw = tk.Toplevel(self)
                tw.attributes('-topmost', True)
                tw.title('transactions')
                l = tk.Label(tw)
                l.pack()
                t = [(a, b) for (a, b) in tr if b]
                m = str(max([len(b) for (_, b) in t]) if t else 1)
                s = 't({})\t{:>%s}' % m
                tl = [s.format(a, b) for (a, b) in t]
                l.configure(text='\n'.join(tl))


class LBRBText(tk.Text):
    '''класс виджета (5)LB/RB'''
    bounds = {}.fromkeys(['LB', 'RB'])  # LB/RB instance
    info_text = {'LB': '(5) LB | строк=%s | длина=%s', 'RB': '(5) RB | строк=%s | длина=%s'}

    def __init__(self, name: str, parent: object):
        self.heightVar = tk.IntVar(value=defaults.DEFAULT_LB_RB_MIN_HEIGHT)

        self.label_info = tk.LabelFrame(
            parent, text=self.info_text[name], font=defaults.DefaultFont + ' bold italic', padx=0, pady=0,
            relief='groove', labelanchor=tk.N, bd=4)
        self.label_info.grid_rowconfigure(0, weight=1)
        self.label_info.grid_columnconfigure(0, weight=1)

        super().__init__(
            self.label_info, height=defaults.DEFAULT_LB_RB_MIN_HEIGHT, background=defaults.Background,
            font=defaults.DefaultLBRBFont, wrap=tk.NONE, padx=0, pady=0)
        self.name = name

        self.bounds[name] = self

        self.scrolly = ttk.Scrollbar(self.label_info, orient=tk.VERTICAL, command=self.yview)
        self.scrollx = ttk.Scrollbar(self.label_info, orient=tk.HORIZONTAL, command=self.xview)
        self.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set, bd=0, padx=0, pady=0)

    def get(self, index1=1.0, index2='end') -> str:
        '''текущий LB/RB'''
        return super().get(index1, index2)[:-1]  # [:-1] - '\n'

    def set(self, text: str) -> None:
        '''задать LB/RB'''
        self.delete(1.0, 'end')
        self.insert(1.0, text)
        try:
            self.label_info['text'] = self.info_text[self.name] % (len(text.split('\n')), len(text))
        except TypeError:
            self.label_info['text'] = self.info_text[self.name] % (len(text.decode().split('\n')), len(text))

    @classmethod
    def set_LB_RB(cls, *args) -> None:
        '''извлечь LB/RB из файла'''
        cls.set_label_text()

        lb = defaults.VarLB.get()
        try:
            cls.bounds['LB'].set(lb)
        except Exception as ex:
            lr_log.Logger.error('LB {}'.format(ex.args))
            cls.bounds['LB'].set(lb.encode(defaults.VarEncode.get(), errors='replace'))

        rb = defaults.VarRB.get()
        try:
            cls.bounds['RB'].set(rb)
        except Exception as ex:
            lr_log.Logger.error('RB {}'.format(ex.args))
            cls.bounds['RB'].set(lb.encode(defaults.VarEncode.get(), errors='replace'))

    @classmethod
    def set_label_text(cls) -> None:
        '''сброс label-текста'''
        for b in cls.info_text:
            cls.bounds[b].label_info['text'] = cls.info_text[b]

    def set_height(self) -> None:
        '''кол-во строк LB/RB'''
        self.configure(height=self.heightVar.get())


def highlight_mode(widget, word: str, option='background', color='cyan') -> None:
    '''залить цветом все word в tk.Text widget'''
    colors = widget.highlight_dict.setdefault(option, {})
    try:
        colors[color].add(word)
    except (KeyError, AttributeError):
        colors[color] = {word}
