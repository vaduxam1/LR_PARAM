# -*- coding: UTF-8 -*-
# gui виджет цветного текста с номерами линий

import re
import copy
import tkinter as tk
from tkinter.font import Font

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.widj.highlight as lr_highlight


class HighlightText(tk.Text):
    '''tk.Text'''
    def __init__(self, *args, **kwargs):
        bind = kwargs.pop('bind', None)
        super().__init__(*args, **kwargs)
        self.action = args[0]  # parent

        self.highlight_dict = copy.deepcopy(lr_vars.VarDefaultColorTeg)
        self.highlight_lines = lr_highlight.HighlightLines(self, self.get_tegs_names())

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
        w = ('bold' if self.weight_var.get() else 'normal')
        s = ('italic' if self.slant_var.get() else 'roman')
        u = (1 if self.underline_var.get() else 0)
        o = (1 if self.overstrike_var.get() else 0)
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
            self.highlight_lines = lr_highlight.HighlightLines(self, self.get_tegs_names())
            self.action.report_position()  # показать

    def get_tegs_names(self) -> {str: {str,}}:
        '''_tegs_names + \\xCE\\xE1'''
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
