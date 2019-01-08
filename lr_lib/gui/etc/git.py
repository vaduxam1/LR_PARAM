# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import threading
import tkinter.messagebox
import urllib.request

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.wrsp.main_window


def init(c_args=None) -> None:
    """создать gui"""
    print(c_args)
    lr_vars.Window = lr_lib.gui.wrsp.main_window.Window()  # main Gui


    return


def _git_update_check():
    t = threading.Thread(target=check_git_ver)
    t.start()
    return


def start(action=True, lock=True) -> None:
    """action + lock"""
    if action:  # action Gui
        lr_vars.Window.new_action_window()  # lr_lib.gui.action.main_action.ActionWindow()
    if lock:  # main thread lock
        lr_vars.Tk.mainloop()
    return


def find_git_ver():
    """версия утилиты на github.com"""
    with urllib.request.urlopen(lr_vars.GitHub) as f:
        html = f.read().decode('utf-8')

    v = html.split('>VERSION</span>', 1)
    v = v[1].split('\n', 1)
    v = v[0].split('</span>v', 1)
    v = v[1].split('<', 1)
    GVER = 'v{0}'.format(v[0])
    return GVER


def check_git_ver():
    """проверить обновление версии утилиты на github.com"""
    GVER = find_git_ver()
    lr_vars.Logger.info([lr_vars.github, GVER])
    if lr_vars.VERSION != GVER:
        tkinter.messagebox.showwarning(
            "Для версии {v} доступно обновление".format(v=lr_vars.VERSION),
            "По адресу {a} доступно последнее [{v}] обновление утилиты.".format(
                v=GVER,a=lr_vars.github,
            ))
    return