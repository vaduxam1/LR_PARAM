﻿# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import threading

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.wrsp.main_window


def init(c_args=None) -> None:
    """создать gui"""
    print(c_args)
    lr_vars.Window = lr_lib.gui.wrsp.main_window.Window()  # main Gui

    t = threading.Thread(target=lr_vars.check_git_ver)
    t.start()
    return


def start(action=True, lock=True) -> None:
    """action + lock"""
    if action:  # action Gui
        lr_vars.Window.new_action_window()  # lr_lib.gui.action.main_action.ActionWindow()
    if lock:  # main thread lock
        lr_vars.Tk.mainloop()
    return
