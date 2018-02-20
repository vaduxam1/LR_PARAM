# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.wrsp.main_window as lr_window
import lr_lib.gui.action.main_action as lr_action
import lr_lib.gui.action.act_other as lr_act_other
import lr_lib.core.wrsp.files as lr_files


def init(mainloop_lock=True, action=True) -> None:
    '''создать gui и заблокировать __main__'''
    lr_vars.MainThreadUpdater.submit(lr_files.init)  # файлы

    lr_vars.Window = lr_window.Window()  # gui

    if action and lr_act_other.get_action_file(file='action.c'):
        lr_action.ActionWindow()

    if mainloop_lock:  # lock
        lr_vars.Tk.mainloop()
