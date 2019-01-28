# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import threading
import tkinter.messagebox
import urllib.request

import lr_lib.core.var.vars as lr_vars


def _git_update_check():
    t = threading.Thread(target=check_git_ver)
    t.start()
    return


def find_git_ver():
    """версия утилиты на github.com"""
    if not lr_vars.githubCheckUpdateEnable:
        return

    with urllib.request.urlopen(lr_vars.GitHub) as f:
        html = f.read().decode('utf-8')

    v = html.split('>VERSION</span>', 1)
    v = v[1].split('\n', 1)
    v = v[0].split('</span>v', 1)
    v = v[1].split('<', 1)

    ver = 'v{0}'.format(v[0])
    return ver


def check_git_ver():
    """проверить обновление версии утилиты на github.com"""
    GVER = find_git_ver()
    lr_vars.Logger.info([lr_vars.github, GVER])
    if lr_vars.VERSION != GVER:
        tkinter.messagebox.showwarning(
            "Для версии {v} доступно обновление".format(v=lr_vars.VERSION),
            "По адресу {a} доступно последнее [{v}] обновление утилиты.".format(
                v=GVER, a=lr_vars.github,
            ))
    return
