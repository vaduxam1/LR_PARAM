# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.wrsp.main_window as lr_window


def init(action=True) -> None:
    """создать gui и заблокировать __main__"""
    lr_vars.Window = lr_window.Window()  # main Gui
    if action:  # action Gui
        lr_vars.Window.new_action_window()  # lr_lib.gui.action.main_action.ActionWindow()


def start() -> None:
    """main thread lock"""
    lr_vars.Tk.mainloop()
