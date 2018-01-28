# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.wrsp.main_window as lr_window
import lr_lib.gui.action.main_action as lr_action


def init(mainloop_lock=True, action=True, auto_param_creator=False) -> None:
    '''создать gui и заблокировать __main__'''
    lr_vars.Window = lr_window.Window()

    if action and lr_action.get_action_file(file='action.c'):
        lr_action.ActionWindow()

    if mainloop_lock:
        lr_vars.Tk.mainloop()
