# -*- coding: UTF-8 -*-
# gui виджет цветного текста с номерами линий

import re
import copy
import threading

import tkinter as tk

from tkinter.font import Font

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.widj.highlight as lr_highlight
import lr_lib.core.action.web_ as lr_web_


class HighlightText(tk.Text):
    """Colored tk.Text + line_numbers"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.action = args[0]  # parent

        self.bind_all("<Control-z>", self.undo)
        self.bind_all("<Control-y>", self.redo)

        self.highlight_dict = copy.deepcopy(lr_vars.VarDefaultColorTeg)

        self.font_var = tk.StringVar(value=kwargs.get('font_var', lr_vars.DefaultActionNoHighlightFont))
        self.size_var = tk.IntVar(value=kwargs.get('size_var', lr_vars.DefaultActionNoHighlightFontSize))
        self.weight_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontBold)
        self.underline_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontUnderline)
        self.slant_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontSlant)
        self.overstrike_var = tk.BooleanVar(value=lr_vars.DefaultActionNoHighlightFontOverstrike)

        self.highlight_var = tk.BooleanVar(value=lr_vars.HighlightOn)

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
        self.highlight_lines = lr_highlight.HighlightLines(self, self.get_tegs_names())
        self.set_tegs()

    def init(self):
        """пересоздать self.highlight_lines"""
        self.highlight_lines = lr_highlight.HighlightLines(self, self.get_tegs_names())

    def undo(self, event):
        return self.edit_undo()

    def redo(self, event):
        return self.edit_redo()

    def new_text_set(self, text: str) -> None:
        """заменить весь текст на новый"""
        self.delete(1.0, tk.END)
        self.insert(1.0, text)

    def _text_checkbox(self) -> (str, str, int, int):
        """text checkbox's get,
        + дополнительно используется как self.__class__._text_checkbox(parent) - color/nocolor?"""
        w = ('bold' if self.weight_var.get() else 'normal')
        s = ('italic' if self.slant_var.get() else 'roman')
        u = (1 if self.underline_var.get() else 0)
        o = (1 if self.overstrike_var.get() else 0)
        return w, s, u, o,

    def set_tegs(self, *a, remove=False, parent=None, ground=('background', 'foreground',)) -> None:
        """создать/удалить теги, для parent/self"""
        if remove:
            for tag in self.tag_names():
                if any(tag.startswith(g) for g in ground):
                    self.tag_delete(tag)
            return

        if parent is None:
            parent = self

        tegs = lr_vars.VarColorTeg.get()
        w, s, u, o = self.__class__._text_checkbox(parent)

        size = parent.size_var.get()
        f = Font(family=parent.font_var.get(), size=size, weight=w, slant=s, underline=u, overstrike=o)

        for g in ground:
            for color in tegs:
                self.tag_config(g + color, **{g: color, 'font': f, })

    def reset_highlight(self, highlight=True) -> None:
        """сбросить текст настройки цветов"""
        self.highlight_dict.clear()
        self.highlight_dict.update(copy.deepcopy(lr_vars.VarDefaultColorTeg))
        if highlight:
            self.highlight_apply()

    def set_font(self, *a, size=None) -> None:
        if size is None:
            size = self.size_var.get()
        w, s, u, o = self._text_checkbox()
        self.configure(font=Font(family=self.font_var.get(), size=size, weight=w, slant=s, underline=u, overstrike=o))

    def highlight_apply(self, *a) -> None:
        """tk.Text tag_add/remove, сформировать on_screen_lines "карту" подсветки"""
        self.highlight_lines.set_thread_attrs()
        self.set_tegs(remove=True)

        if self.highlight_var.get():
            self.set_tegs(remove=False, parent=self)
            self.set_tegs(remove=False, parent=self.action)

            self.init()
            self.action.report_position()  # показать

    def get_tegs_names(self) -> {str: {str,}}:
        """_tegs_names + \\xCE\\xE1"""
        tegs_names = {}
        hex_unicode_words = re.compile('\\\\x\w\w').findall(self.get(1.0, tk.END))  # \\xCE\\xE1
        self.highlight_dict.setdefault(
            lr_vars.hex_unicode_ground, dict()).setdefault(lr_vars.hex_unicode_color, set()).update(hex_unicode_words)

        for ground in self.highlight_dict:
            colors = self.highlight_dict[ground]
            for color in colors:
                tag = ground + color
                for name in colors[color]:

                    task = (name.lower(), len(name))  # name.lower() !
                    try:
                        tegs_names[tag].add(task)
                    except (KeyError, AttributeError):
                        tegs_names[tag] = {task}

        wrsp_all = tuple(self.action.web_action.get_web_reg_save_param_all())
        ps = self.action.web_action.websReport.param_statistic
        for wr in wrsp_all:
            n = wr.name
            if (n in ps) and (not all(ps[n].values())):
                self.highlight_mode(wr.name, option='background', color='yellow')

        for n in self.action.web_action.transactions.names:
            self.highlight_mode(n, option='foreground', color='darkslategrey')

        return tegs_names

    def web_add_highlight(self, web_) -> None:
        """подсветить web_"""
        self.highlight_mode(web_.type)

        for line in web_.comments.split('\n'):
            self.highlight_mode(line.strip())

        if isinstance(web_, lr_web_.WebRegSaveParam):
            m = lr_vars.web_reg_highlight_len
            self.highlight_mode('{}'.format(web_.name[:m]), option='background', color=lr_vars.wrsp_color1)
            self.highlight_mode(web_.name[m:], option='foreground', color=lr_vars.wrsp_color2)
            self.highlight_mode(web_.param, option='foreground', color=lr_vars.wrsp_color2)
            for line in web_.lines_list[1:]:
                self.highlight_mode(line.strip())
        else:
            self.highlight_mode(web_.name)

    def highlight_mode(self, word: str, option='foreground', color=lr_vars.DefaultColor) -> None:
        """залить цветом все word в tk.Text widget"""
        colors = self.highlight_dict.setdefault(option, {})
        try:
            colors[color].add(word)
        except (KeyError, AttributeError):
            colors[color] = {word}


class TextLineNumbers(tk.Canvas):
    """номера линий tk.Text"""
    def __init__(self, tk_text: HighlightText):
        super().__init__(tk_text.action, background=lr_vars.Background)
        self.linenum = -1

        self.tk_text = tk_text

    def redraw(self, *args, __restart=False) -> None:
        """redraw line numbers"""
        self.delete("all")
        self.linenum = 0

        i = self.tk_text.index("@0,0")
        while True:
            dline = self.tk_text.dlineinfo(i)
            if dline is None:
                break

            y = dline[1]
            self.linenum = str(i).split(".", 1)[0]
            self.create_text(2, y, anchor="nw", text=self.linenum)
            i = self.tk_text.index("%s+1line" % i)
