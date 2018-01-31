# -*- coding: UTF-8 -*-
# всякое для gui


def center_widget(widget) -> None:
    '''center window on screen'''
    widget.withdraw()
    widget.update_idletasks()
    x = (widget.winfo_screenwidth() - widget.winfo_reqwidth()) / 2
    y = (widget.winfo_screenheight() - widget.winfo_reqheight()) / 2
    widget.geometry("+%d+%d" % (x, y))
    widget.deiconify()
