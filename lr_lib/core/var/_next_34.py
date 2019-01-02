# -*- coding: UTF-8 -*-
# не используется, приведен как пример
# все варианты смены VarPartNum и VarFile

import lr_lib
import lr_lib.core.wrsp.param
import lr_lib.core.var.vars as lr_vars


def all_wrsp_variant() -> iter(([dict, str], )):
    for _ in next_part_or_file():
        wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
        web_reg_save_param = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)

        item = [wrsp_dict, web_reg_save_param]
        yield item
        continue
    return


def next_part_or_file(_work=True) -> iter((bool, )):
    """
    все варианты param-вхождений и файлов
    """
    yield
    while _work:
        if _next_part():
            yield True
        elif _next_file():
            yield False
        else:
            break
        continue
    return


def _next_part() -> bool:
    """следующее param-вхождение"""
    file = lr_vars.VarFile.get()
    count = file['Param']['Count']
    num = (lr_vars.VarPartNum.get() + 1)
    if num < count:  # вхождение(4)
        lr_vars.VarPartNum.set(num)
        return True
    return False


def _next_file() -> bool:
    """следующей файл"""
    f = lr_vars.VarFile.get()
    index = lr_vars.FilesWithParam.index(f)
    try:
        file = lr_vars.FilesWithParam[index + 1]
    except IndexError:
        return False
    else:
        lr_vars.VarFile.set(file)
    return True
