# -*- coding: UTF-8 -*-
# gui виджет цветного текста с номерами линий

import copy
import re
import tkinter as tk
from tkinter.font import Font
from typing import Iterable, Tuple, List, Dict, Set

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.gui.widj.highlight


class HighlightText(tk.Text):
    """
    Colored tk.Text + line_numbers
    """

    def __init__(self, action: 'lr_lib.gui.action.main_action.ActionWindow', *args, **kwargs):
        super().__init__(action, *args, undo=True, maxundo=lr_vars.maxundo, autoseparators=True, **kwargs)
        self.cursor_position = self.index(tk.INSERT)  # координаты текущей позиции в tk.Text

        self.action = action  # parent

        self.highlight_dict = copy.deepcopy(lr_lib.core.var.vars_highlight.VarDefaultColorTeg)

        self.font_var = tk.StringVar(value=kwargs.get('font_var', lr_vars.DefaultActionNoHighlightFont))
        self.size_var = tk.IntVar(value=kwargs.get('size_var', lr_vars.DefaultActionNoHighlightFontSize))
        self.weight_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontBold)
        self.underline_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontUnderline)
        self.slant_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontSlant)
        self.overstrike_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontOverstrike)

        self.highlight_var = tk.BooleanVar(value=lr_lib.core.var.vars_highlight.HighlightOn)

        self.tk.eval("""
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
                            """)
        self.tk.eval("""
                            rename {widget} _{widget}
                            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
                        """.format(widget=str(self)))

        # номера линий
        self.linenumbers = TextLineNumbers(self)

        self.bind("<<Change>>", self.linenumbers.redraw)
        self.bind("<Configure>", self.linenumbers.redraw)

        # кдасс подсветки текста
        self.highlight_lines = self.init()
        self.set_tegs()
        return

    def init(self) -> lr_lib.gui.widj.highlight.HighlightLines:
        """
        пересоздать self.highlight_lines
        """
        tn = self.get_tegs_names()
        self.highlight_lines = lr_lib.gui.widj.highlight.HighlightLines(self, tn)
        self.linenumbers.add_linenumbers()  # "тип" линии, для показа в TextLineNumbers
        return self.highlight_lines

    def after_callback(self) -> None:
        """
        подсветить все линии на экране, и перезапустить
        """
        try:
            self.cursor_position = self.index(tk.INSERT)
        except tk.TclError as ex:
            return  # закрытие action окна

        if self.action.id_ in lr_vars.Window.action_windows:  # перезапустить
            self.highlight_lines.highlight_callback()
            lr_vars.Tk.after(self.highlight_lines.HighlightAfter0, self.after_callback)
        return

    def new_text_set(self, text: str) -> None:
        """
        заменить весь текст на новый
        """
        self.delete(1.0, tk.END)
        self.insert(1.0, text)
        return

    def _text_checkbox(self) -> Tuple[str, str, int, int]:
        """
        text checkbox's get,
        + дополнительно используется как self.__class__._text_checkbox(parent) - color/nocolor?
        """
        w = ('bold' if self.weight_var.get() else 'normal')
        s = ('italic' if self.slant_var.get() else 'roman')
        u = (1 if self.underline_var.get() else 0)
        o = (1 if self.overstrike_var.get() else 0)
        ww = (w, s, u, o,)
        return ww

    def set_tegs(self, *a, remove=False, parent=None, ground=('background', 'foreground',)) -> None:
        """
        создать/удалить теги, для parent/self
        """
        if remove:
            for tag in self.tag_names():
                if any(tag.startswith(g) for g in ground):
                    self.tag_delete(tag)
                continue
            return

        if parent is None:
            parent = self

        tegs = lr_lib.core.var.vars_highlight.VarColorTeg.get()
        (w, s, u, o) = self.__class__._text_checkbox(parent)

        size = parent.size_var.get()
        ff = parent.font_var.get()
        fnt = Font(family=ff, size=size, weight=w, slant=s, underline=u, overstrike=o)

        for g in ground:
            for color in tegs:
                dc = {g: color, 'font': fnt, }
                gd = (g + color)
                self.tag_config(gd, **dc)
                continue
            continue
        return

    def reset_highlight(self, highlight=True) -> None:
        """
        сбросить текст настройки цветов
        """
        self.highlight_dict.clear()
        d = copy.deepcopy(lr_lib.core.var.vars_highlight.VarDefaultColorTeg)
        self.highlight_dict.update(d)
        if highlight:
            self.highlight_apply()
        return

    def set_font(self, *a, size=None) -> None:
        """
        получить переменные шрифтов
        """
        if size is None:
            size = self.size_var.get()
        (w, s, u, o) = self._text_checkbox()
        ff = self.font_var.get()
        f = Font(family=ff, size=size, weight=w, slant=s, underline=u, overstrike=o)
        self.configure(font=f)
        return

    def highlight_apply(self, *a) -> None:
        """
        tk.Text tag_add/remove, сформировать on_screen_lines "карту" подсветки
        """
        self.highlight_lines.set_thread_attrs()
        self.set_tegs(remove=True)

        if self.highlight_var.get():
            self.set_tegs(remove=False, parent=self)
            self.set_tegs(remove=False, parent=self.action)

            self.init()
            self.action.report_position()  # показать
        return

    def get_tegs_names(self) -> Dict[str, Set[Tuple[str, int]]]:
        """
        _tegs_names + \\xCE\\xE1
        """
        tegs_names = {}
        hex_unicode_words = re.compile(lr_lib.core.var.vars_highlight.hex_unicode_words).findall(
            self.get(1.0, tk.END))  # \\xCE\\xE1
        self.highlight_dict.setdefault(
            lr_lib.core.var.vars_highlight.hex_unicode_ground, dict()).setdefault(
            lr_lib.core.var.vars_highlight.hex_unicode_color, set()).update(hex_unicode_words)

        for ground in self.highlight_dict:
            colors = self.highlight_dict[ground]
            for color in colors:
                tag = (ground + color)
                for name in colors[color]:

                    task = (name.lower(), len(name))  # name.lower() !
                    try:
                        tegs_names[tag].add(task)
                    except (KeyError, AttributeError):
                        tegs_names[tag] = {task}
                    continue
                continue
            continue

        wrsp_all = tuple(self.action.web_action.get_web_reg_save_param_all())
        ps = self.action.web_action.websReport.param_statistic
        for wr in wrsp_all:  # warn_wrsp highlight
            n = wr.name
            if (n in ps) and (not all(ps[n].values())):
                self.highlight_mode(wr.name, option='background', color=lr_lib.core.var.vars_highlight.color_warn_wrsp)
            continue

        for n in self.action.web_action.transactions.names:
            self.highlight_mode(n, option='foreground', color=lr_lib.core.var.vars_highlight.color_transactions_names)
            continue

        return tegs_names

    def web_add_highlight(self, web_: 'lr_lib.core.action.web_.WebSnapshot') -> None:
        """
        подсветить web_
        """
        self.highlight_mode(web_.type)

        for line in web_.comments.split('\n'):
            self.highlight_mode(line.strip())
            continue

        if isinstance(web_, lr_lib.core.action.web_.WebRegSaveParam):
            m = lr_lib.core.var.vars_highlight.web_reg_highlight_len
            t = '{}'.format(web_.name[:m])
            self.highlight_mode(t, option='background', color=lr_lib.core.var.vars_highlight.wrsp_color1, )
            self.highlight_mode(web_.name[m:], option='foreground', color=lr_lib.core.var.vars_highlight.wrsp_color2)
            self.highlight_mode(web_.param, option='foreground', color=lr_lib.core.var.vars_highlight.wrsp_color2)
            for line in web_.lines_list[1:]:
                self.highlight_mode(line.strip())
                continue
        else:
            self.highlight_mode(web_.name)
        return

    def highlight_mode(self, word: str, option='foreground', color=lr_lib.core.var.vars_highlight.DefaultColor) -> None:
        """
        залить цветом все word в tk.Text widget
        """
        colors = self.highlight_dict.setdefault(option, {})
        try:
            colors[color].add(word)
        except (KeyError, AttributeError):
            colors[color] = {word}
        return


class TextLineNumbers(tk.Canvas):
    """
    номера линий tk.Text
    """

    def __init__(self, tk_text: 'HighlightText'):
        super().__init__(tk_text.action, background=lr_lib.core.var.vars_highlight.Background)
        self.linenum = -1
        self.linenumbers = {}  # {1: str, 2: WebSnapshot, }  связь номеров линий, и типа находящегося там контента
        self.tk_text = tk_text
        return

    def redraw(self, *args, __restart=False) -> None:
        """
        redraw line numbers
        """
        self.delete("all")
        self.linenum = 0

        i = self.tk_text.index("@0,0")
        while True:
            dline = self.tk_text.dlineinfo(i)
            if dline is None:
                break

            y = dline[1]
            linenum = str(i).split(".", 1)[0]
            linenum = int(linenum)  # номер линии

            try:  # "тип" линии
                line_type = self.linenumbers[linenum]
            except KeyError as ex:
                line_type = ''

            self.linenum = '{linenum} {line_type}'.format(linenum=linenum, line_type=line_type, )
            self.create_text(2, y, anchor="nw", text=self.linenum)

            i = self.tk_text.index("%s+1line" % i)
            continue
        return

    def add_linenumbers(self) -> None:
        """
        создать self.linenumbers: line_num += 1 : для каждого '\n'
        """
        self.linenumbers.clear()
        text = self.tk_text.get('1.0', tk.END)
        split = text.split('\n')

        for (line_num, line) in enumerate(split, start=1):
            line_type = self.get_line_type(line)
            self.linenumbers[line_num] = line_type
            continue
        return

    def get_line_type(self, line: str, i=10) -> str:
        """определить "тип" линии, для показа в TextLineNumbers"""
        line = line.strip()
        if line.startswith('web_reg_save_param'):
            if 'web_reg_save_param("' in line:
                s = line.split('web_reg_save_param("', 1)[1]
                s = s.split('"', 1)[0].strip()
            else:
                s = 'P'
            t = '+{%s} '
            t = (t % s[:9])
        elif line.startswith('"Snapshot=t'):
            t = line.split('"Snapshot=t', 1)[1]
            t = t.split('.', 1)[0]
            t = 'inf={0}'.format(t)
        elif line.startswith('web_'):
            t = ' _( web )_'
        elif line.startswith('lr_start_transaction'):
            t = ('>' * i)
        elif line.startswith('lr_end_transaction'):
            t = ('<' * i)
        elif line.startswith('lr_'):
            t = ' [ lr ]'
        elif '", "Value=' in line:
            t = line.split('", "Value=', 1)[1]
            t = t.split('", ENDITEM,', 1)[0]
            if t.startswith('on'):
                t = t[2:]
            elif t[1:3] == 'on':
                t = t[3:]
            elif t == 'dummy':
                pass  # как есть
            elif any((p in line) for p in self.tk_text.action.web_action.websReport.wrsp_and_param_names):
                t = '={p}'
            elif any(a in line for a in _alst):
                t = ''
            else:
                t = '?'
        elif '\"items\":' in line:
            t = '?'
        else:
            t = ''

        if (not t) and (not line.startswith('//')):
            for p in self.tk_text.action.web_action.websReport.wrsp_and_param_names:
                if p in line:
                    t = '={p}'
                    break
                continue
        return t


_alst = ['pageX', 'left\\":', '{\\"\\":', 'Value=i", ENDITEM', ]
