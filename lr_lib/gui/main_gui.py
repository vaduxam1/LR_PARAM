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
    lr_lib.core.var.vars_highlight.init_highlight_words()  # слова для подсветки

    threading.Thread(target=_git_update_check).start()  # проверить обновление
    return


def _git_update_check():
    """проверить обновление утилиты на github.com"""
    lr_lib.gui.etc.git_update.check_git_ver()
    t = threading.Timer(lr_vars.GitUpdPeriod, _git_update_check)
    t.start()
    return


def start(action=True, lock=True) -> None:
    """action + lock"""
    if action:  # action Gui
        lr_vars.Window.new_action_window()  # lr_lib.gui.action.main_action.ActionWindow()
    if lock:  # main thread lock
        lr_vars.Tk.mainloop()
    return
