# -*- coding: UTF-8 -*-
#  авто-извлечение новых правил поиска {param}, из уже параметризованных LoadRunner-скриптов на диске

import os
from typing import Iterable, Tuple

import lr_lib
import lr_lib.core.action.main_awal
import lr_lib.core.var.vars as lr_vars
from lr_lib.core.var.vars_param import WFILE, LFILE


def find_c_files_from(folder=os.getcwd(), ext='.c') -> Iterable[str]:
    """
    поиск *.c файлов
    :param folder: srt: 'C:\\SCR\\'
    :param ext: str: '.c'
    :return: Iterable["C:\SCR\LR_11\action.c"]
    """
    for (root, dirs, files) in os.walk(folder):
        for f in files:
            if f.endswith(ext):
                file = os.path.join(root, f)
                yield file
            continue
        continue
    return


def read_c_file(file: str, action=None, enc=lr_lib.core.var.etc.vars_other.VarEncode.get()) -> Iterable:
    """
    гайти LB и начала имен param, из файла
    :param file: str: "C:\SCR\LR_11\action.c"
    :param action: 'lr_lib.gui.action.main_action.ActionWindow'
    :return: Iterable[(file, (name, lb))]
    """
    _web_action = lr_lib.core.action.main_awal.ActionWebsAndLines(action)

    with open(file, encoding=enc, errors='replace') as f:
        text = f.read()

    _web_action.set_text_list(text)
    wrsps = tuple(_web_action.get_web_reg_save_param_all())
    m = lr_vars.SecondaryParamLen.get()

    for w in wrsps:
        wn = w.param[:m]
        if all(map(str.isnumeric, wn)):
            wn = ''
        lb = w.get_lb()

        it = (wn, lb)
        if any(it):
            it = (file, it)
            yield it
        continue

    return ''


def _main3(folder: str) -> Tuple:
    """
    поиск новых LB и начал имен param, из уже готовых скриптов на диске
    :param folder: srt: 'C:\\SCR\\'
    :return: {'bJs', 'REP', 'z__', ...} {'/document_edit.png;jsessionid=",', ...))
    """
    wrsp_part_names = set()
    wrsp_lb = set()
    for file in find_c_files_from(folder):
        for (file, it) in read_c_file(file):
            (wn, lb) = it
            if wn and (wn not in wrsp_part_names):
                wrsp_part_names.add(wn)
            if lb and (lb not in wrsp_lb):
                wrsp_lb.add(lb)
            continue
        continue

    item = (wrsp_part_names, wrsp_lb)
    return item


def main(folder: str) -> Tuple[int, int]:
    """
    поиск новых LB и начал имен param, из уже готовых скриптов на диске
    :param folder: srt: 'C:\\SCR\\'
    :return: None
    """
    s = lr_vars.VarShowPopupWindow.get()
    if s:  # не показывать всплывающие окна ошибок, если проверяемые файлы некорректны
        lr_vars.VarShowPopupWindow.set(False)
    try:
        item = _main2(folder)
    finally:
        lr_vars.VarShowPopupWindow.set(s)
    return item


def _main2(folder: str) -> Tuple[int, int]:
    """
    поиск новых LB и начал имен param, из уже готовых скриптов на диске
    :param folder: srt: 'C:\\SCR\\'
    :return: None
    """
    (wrsp_part_names, wrsp_lb) = _main3(folder)

    fwr = os.path.join(lr_vars.lib_folder, WFILE)
    if os.path.exists(fwr):
        with open(fwr, errors='replace') as f:
            t = f.read()
        t = set(filter(str.strip, t.split('\n')))
        lt1 = len(t)
        t.update(wrsp_part_names)
        lt2 = len(t)
        wr_n = (lt2 - lt1)
        with open(fwr, 'w') as f:
            t = '\n'.join(t)
            f.write(t)
    else:
        with open(fwr, 'w') as f:
            t = '\n'.join(wrsp_part_names)
            f.write(t)
        wr_n = len(wrsp_part_names)

    flb = os.path.join(lr_vars.lib_folder, LFILE)
    if os.path.exists(flb):
        with open(flb, errors='replace') as f:
            t = f.read()
        t = set(filter(str.strip, t.split('\n')))
        bt1 = len(t)
        t.update(wrsp_lb)
        bt2 = len(t)
        lb_n = (bt2 - bt1)
        with open(flb, 'w') as f:
            t = '\n'.join(t)
            f.write(t)
    else:
        with open(flb, 'w') as f:
            t = '\n'.join(wrsp_lb)
            f.write(t)
        lb_n = len(wrsp_lb)

    it = (wr_n, lb_n)
    return it


if __name__ == '__main__':
    dr = 'C:\\SCR\\'
    item = main(dr)
    print(item)
