# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import threading

import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.git_upd
import lr_lib.gui.etc.gui_other
import lr_lib.gui.wrsp.main_window


def init(c_args=None) -> None:
    """
    создать gui
    """
    lr_vars.Window = lr_lib.gui.wrsp.main_window.Window()  # main Gui
    lr_lib.gui.etc.gui_other.wordBreakAfter()  # область выделения двойным кликом мыши

    t = threading.Thread(target=lr_lib.etc.git_upd.git_update_check)
    t.start()  # проверить обновление
    return


def start(action=True, lock=True) -> None:
    """
    action + lock
    """
    if action:  # action Gui
        lr_vars.Window.new_action_window()  # lr_lib.gui.action.main_action.ActionWindow()
    if lock:  # main thread lock
        lr_vars.Tk.mainloop()
    return
