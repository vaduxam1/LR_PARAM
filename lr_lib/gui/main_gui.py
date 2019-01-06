# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import threading

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.gui.etc.git_update
import lr_lib.gui.wrsp.main_window
import lr_lib.gui.etc.gui_other


def init(c_args=None) -> None:
    """создать gui"""
    lr_vars.Window = lr_lib.gui.wrsp.main_window.Window()  # main Gui
    lr_lib.gui.etc.gui_other.wordBreakAfter()  # область выделения двойным кликом мыши

    threading.Thread(target=lr_lib.gui.etc.git_update._git_update_check).start()  # проверить обновление
    return


def start(action=True, lock=True) -> None:
    """action + lock"""
    if action:  # action Gui
        lr_vars.Window.new_action_window()  # lr_lib.gui.action.main_action.ActionWindow()
    if lock:  # main thread lock
        lr_vars.Tk.mainloop()
    return
