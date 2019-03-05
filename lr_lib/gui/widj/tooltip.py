# -*- coding: UTF-8 -*-
# всплывающие подсказки

import collections
import threading
import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight

Lock = threading.Lock()
ActiveTips = collections.OrderedDict()


def tt_clear() -> None:
    """
    удалить все ToolTip
    """
    tips = list(ActiveTips.keys())
    for tip in tips:
        try:
            lr_vars.Tk.after_cancel(ActiveTips[tip])
        except Exception as ex:
            pass
        try:
            tip.hidetip()
        except Exception as ex:
            pass
        try:
            del ActiveTips[tip]
        except Exception as ex:
            pass
        continue
    return


class ToolTip(object):
    """
    всплывающие подсказки
    """

    def __init__(self, widget):
        self.widget = widget
        self.tip = None

        self.x = 0
        self.y = 0
        return

    def showtip(self, text: str) -> None:
        """
        Display text in tooltip
        """
        try:
            (x, y, cx, cy) = self.widget.bbox("insert")
            x += (self.widget.winfo_rootx() + 25)
            y += (self.widget.winfo_rooty() + 20)

            self.tip = tk.Toplevel(self.widget)
            ActiveTips[self] = None

            self.tip.wm_overrideredirect(1)
            self.tip.wm_geometry("+%d+%d" % (x, y))
            self.tip.attributes('-topmost', True)

            lbl = tk.Label(
                self.tip, text=text, justify=tk.LEFT, background=lr_lib.core.var.vars_highlight.Background,
                relief=tk.SOLID, borderwidth=1, font=lr_vars.ToolTipFont,
            )
            lbl.pack(ipadx=0, ipady=0)
        except Exception as ex:
            pass
        return

    def hidetip(self) -> None:
        """
        destroy подсказки
        """
        try:
            self.tip.destroy()
        except Exception as ex:
            pass
        return


def widget_values_counter(widget) -> (int, int):
    """
    кол-во строк/индекс текущей строки виджета
    """
    i = li = 0
    try:
        _i = list(widget['values'])
        w = widget.get()
        i = (_i.index(w) + 1)
    except Exception as ex:
        pass
    try:
        li = len(widget['values'])
    except Exception as ex:
        pass

    item = (widget.widgetName, i, li)
    return item


def createToolTip(widget, text: str) -> None:
    """
    всплывающая подсказка для widget
    """
    toolTip = ToolTip(widget)

    def _enter(event, toolTip=toolTip, text=text, wlines='') -> None:
        """
        событие входа мыши на виджет
        """
        Lock.acquire()
        try:
            tt_clear()
        finally:
            Lock.release()

        wvc = widget_values_counter(widget)
        if any(wvc[1:]):
            wlines = ' * {0} выбрана строка {1} из {2}\n'.format(*wvc)

        t = '{t}{text}'.format(t=wlines, text=text.rstrip(), )
        toolTip.showtip(t)

        t = lr_vars.VarToolTipTimeout.get()
        t = int(t)
        widget.after(t, toolTip.hidetip)
        return

    def leave(event, toolTip=toolTip) -> None:
        """
        событие выхода мыши из виджета
        """
        Lock.acquire()
        try:
            lr_vars.Tk.after_cancel(ActiveTips[toolTip])
        except (KeyError, ValueError, tk.TclError):
            return
        finally:
            toolTip.hidetip()
            Lock.release()
        return

    def enter(event) -> None:
        """
        событие входа мыши на виджет
        """
        Lock.acquire()
        try:
            ActiveTips[toolTip] = lr_vars.Tk.after(lr_vars.TT_WAIT, _enter, event)
        finally:
            Lock.release()
        return

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
    return
