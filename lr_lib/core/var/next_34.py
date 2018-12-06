# -*- coding: UTF-8 -*-
# не используется, как пример смены VarPartNum и VarFile

import lr_lib
import lr_lib.core.var.vars as lr_vars


def next_part_or_file(_work=True):
    yield
    while _work:
        if _next_part():
            yield
        elif _next_file():
            yield
        else:
            break
        continue
    return


def _next_part() -> bool:
    file = lr_vars.VarFile.get()
    count = file['Param']['Count']
    num = (lr_vars.VarPartNum.get() + 1)
    if num < count:  # вхождение(4)
        lr_vars.VarPartNum.set(num)
        return True
    return False


def _next_file() -> bool:
    f = lr_vars.VarFile.get()
    index = lr_vars.FilesWithParam.index(f)
    try:
        file = lr_vars.FilesWithParam[index + 1]
    except IndexError:
        return False
    else:
        lr_vars.VarFile.set(file)
    return True
