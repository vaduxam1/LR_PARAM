# -*- coding: UTF-8 -*-
# всплывающие подсказки

import threading
import contextlib

import tkinter as tk

import lr_lib.core.var.vars as lr_vars


class ToolTip(object):
    '''всплывающие подсказки'''
    toolTips = []
    lock = threading.Lock()

    def __init__(self, widget):
        self.widget = widget
        self.tip = None
        self.x = 0
        self.y = 0

    def showtip(self, text: str) -> None:
        '''Display text in tooltip'''
        if self.toolTips:
            with self.lock:
                for tip in self.toolTips:
                    with contextlib.suppress(Exception):
                        tip.hidetip()
                    with contextlib.suppress(Exception):
                        self.toolTips.remove(tip)

        with self.lock:
            self.toolTips.append(self)

        with contextlib.suppress(Exception):
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            self.tip = tk.Toplevel(self.widget)
            self.tip.wm_overrideredirect(1)
            self.tip.wm_geometry("+%d+%d" % (x, y))
            self.tip.attributes('-topmost', True)
            tk.Label(self.tip, text=text, justify=tk.LEFT, background=lr_vars.Background, relief=tk.SOLID, borderwidth=1,
                     font=lr_vars.ToolTipFont).pack(ipadx=0, ipady=0)

    def hidetip(self) -> None:
        with contextlib.suppress(Exception):
            self.tip.destroy()


def widget_values_counter(widget) -> (int, int):
    '''кол-во строк/индекс текущей строки виджета'''
    i = li = 0

    with contextlib.suppress(Exception):
        _i = list(widget['values'])
        i = _i.index(widget.get()) + 1
    with contextlib.suppress(Exception):
        li = len(widget['values'])

    return widget.widgetName, i, li


def createToolTip(widget, text: str) -> None:
    '''всплывающая подсказка для widget'''
    toolTip = ToolTip(widget)

    def enter(event, toolTip=toolTip, text=text, wlines='') -> None:
        wvc = widget_values_counter(widget)
        if any(wvc[1:]):
            wlines = ' * {0} выбрана строка {1} из {2}\n'.format(*wvc)

        toolTip.showtip('{t}{text}'.format(t=wlines, text=text.rstrip()))
        widget.after(int(lr_vars.VarToolTipTimeout.get()), toolTip.hidetip)  # тк иногда подсказки "зависают"

    def leave(event, toolTip=toolTip) -> None:
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
