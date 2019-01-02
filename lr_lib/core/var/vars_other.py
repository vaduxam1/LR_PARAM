# -*- coding: UTF-8 -*-
# общие переменные, настройки - разное

import encodings.aliases
import functools
import string
import tkinter as tk

import lr_lib.core.var.vars

#####################################
# все кодировки
VarEncode = tk.StringVar(value='cp1251')  # используемая кодировка файлов
ENCODE_LIST = {
    'base64_codec', 'bz2_codec', 'cp1006', 'cp65001', 'cp720', 'cp737', 'cp856', 'cp874', 'cp875', 'hex_codec',
    'hp_roman8', 'koi8_u', 'mbcs', 'quopri_codec', 'rot_13', 'tactis', 'tis_620', 'utf_8_sig', 'uu_codec', 'zlib_codec',
}
ENCODE_LIST.update(set(encodings.aliases.aliases.values()))
ENCODE_LIST = list(sorted(ENCODE_LIST))

#####################################
# уровни логирования
loggingLevels = {
    'TRACE': 1,
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50,
}


#####################################
# functions


def _unpunct(st: str) -> str:
    """без пунктуации в конце строки"""
    if st:
        if st[-1] in string.punctuation:
            return _unpunct(st[:-1])
        else:
            return st
    return ''


def T_POOL_decorator(func: callable):
    """декоратор, выполнения func в T_POOL потоке"""

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if hasattr(lr_lib.core.var.vars.T_POOL, 'submit'):
            out = lr_lib.core.var.vars.T_POOL.submit(func, *args, **kwargs)
        elif hasattr(lr_lib.core.var.vars.T_POOL, 'apply_async'):
            out = lr_lib.core.var.vars.T_POOL.apply_async(func, args, kwargs)
        else:
            raise AttributeError('у пула({p}) нет атрибута submit или apply_async\n{f}\n{a}\n{k}'.format(
                f=func, a=args, k=kwargs, p=lr_lib.core.var.vars.T_POOL.pool))
        return out
    return wrap


VRS = (
    lr_lib.core.var.vars.VarParam,
    lr_lib.core.var.vars.VarFileName,
    lr_lib.core.var.vars.VarFile,
    lr_lib.core.var.vars.VarPartNum,
    lr_lib.core.var.vars.VarLB,
    lr_lib.core.var.vars.VarRB,
    lr_lib.core.var.vars.VarFileText,
    lr_lib.core.var.vars.VarWrspDict,
    lr_lib.core.var.vars.VarFileSortKey1,
    lr_lib.core.var.vars.VarFileSortKey2,
)  # переменные для default_value очистки


def clearVars() -> None:
    """очистка Var's"""
    for var in VRS:
        var.set(var.default_value, callback=False)
        continue
    lr_lib.core.var.vars.FilesWithParam.clear()
    return
