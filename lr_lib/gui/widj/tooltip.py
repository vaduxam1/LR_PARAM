# -*- coding: UTF-8 -*-
# всплывающие подсказки

import threading

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_h


class ToolTip(object):
    """всплывающие подсказки"""
    toolTips = []
    lock = threading.Lock()

    def __init__(self, widget):
        self.widget = widget
        self.tip = None
        self.x = 0
        self.y = 0
        return

    def showtip(self, text: str) -> None:
        """Display text in tooltip"""
        if self.toolTips:
            with self.lock:
                for tip in self.toolTips:
                    try:
                        tip.hidetip()
                    except Exception as ex:
                        pass
                    try:
                        self.toolTips.remove(tip)
                    except Exception as ex:
                        pass
                    continue

        with self.lock:
            self.toolTips.append(self)

        try:
            (x, y, cx, cy) = self.widget.bbox("insert")
            x += (self.widget.winfo_rootx() + 25)
            y += (self.widget.winfo_rooty() + 20)
            self.tip = tk.Toplevel(self.widget)
            self.tip.wm_overrideredirect(1)
            self.tip.wm_geometry("+%d+%d" % (x, y))
            self.tip.attributes('-topmost', True)
            tk.Label(self.tip, text=text, justify=tk.LEFT, background=lr_lib.core.var.vars_h.Background, relief=tk.SOLID, borderwidth=1,
                     font=lr_vars.ToolTipFont).pack(ipadx=0, ipady=0)
        except Exception as ex:
            pass
        return

    def hidetip(self) -> None:
        try:
            self.tip.destroy()
        except Exception as ex:
            pass
        return


def widget_values_counter(widget) -> (int, int):
    """кол-во строк/индекс текущей строки виджета"""
    i = li = 0
    try:
        _i = list(widget['values'])
        i = (_i.index(widget.get()) + 1)
    except Exception as ex:
        pass
    try:
        li = len(widget['values'])
    except Exception as ex:
        pass

    return widget.widgetName, i, li


def createToolTip(widget, text: str) -> None:
    """всплывающая подсказка для widget"""
    toolTip = ToolTip(widget)

    def enter(event, toolTip=toolTip, text=text, wlines='') -> None:
        wvc = widget_values_counter(widget)
        if any(wvc[1:]):
            wlines = ' * {0} выбрана строка {1} из {2}\n'.format(*wvc)

        toolTip.showtip('{t}{text}'.format(t=wlines, text=text.rstrip()))
        widget.after(int(lr_vars.VarToolTipTimeout.get()), toolTip.hidetip)  # тк иногда подсказки "зависают"
        return

    def leave(event, toolTip=toolTip) -> None:
        toolTip.hidetip()
        return

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
    return
