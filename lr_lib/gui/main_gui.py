# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.git_upd
import lr_lib.gui.etc.gui_other
import lr_lib.gui.wrsp.main_window


def init(c_args=None) -> None:
    """
    создать gui
    """
    if c_args:
        lr_vars.Logger.debug(c_args)

    # main Gui
    lr_vars.Window = lr_lib.gui.wrsp.main_window.Window()

    lr_lib.gui.etc.gui_other.wordBreakAfter()  # область выделения двойным кликом мыши
    lr_lib.etc.git_upd.git_update_check()  # проверить обновление
    return


def start(new_action_window=True, ) -> None:
    """
    action + lock
    """
    if new_action_window:  # action окно
        lr_vars.Window.new_action_window()  # lr_lib.gui.action.main_action.ActionWindow()

    # блокировать главный поток
    lr_vars.Tk.mainloop()
    return
