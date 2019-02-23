# -*- coding: UTF-8 -*-
# не используется, приведен как пример получения web_reg_save_param,
#   для всех возможных вариантов VarPartNum/VarFile

from typing import Iterable, Tuple

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param


def all_wrsp_variant() -> Iterable[Tuple[dict, str]]:
    """
    получить web_reg_save_param, для всех вариантов VarPartNum/VarFile
    """
    for _ in next_part_or_file():
        item = wrsp_item()
        yield item  # web_reg_save_param
        continue
    return


def wrsp_item() -> Tuple[dict, str]:
    """
    сформировать web_reg_save_param
    """
    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()  # dict с данными для формирования WRSP
    web_reg_save_param = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)  # WRSP для вставки в LR
    item = (wrsp_dict, web_reg_save_param)
    return item


def next_part_or_file(_work=True) -> Iterable[bool]:
    """
    все варианты param-вхождений и файлов
    True - смена вхождения(4) / False - смена файла(3)
    """
    yield  # первый раз ничего не менять, для учета текущего установленного варианта VarPartNum/VarFile
    while _work:  # затем смена VarPartNum, при окончании VarPartNum - смена VarFile, и опять менять VarPartNum
        if _next_part():
            yield True  # (4)
        elif _next_file():
            yield False  # (3)
        else:
            break  # все варианты перебраны
        continue
    return


def _next_part() -> bool:
    """
    следующее param-вхождение(4)
    """
    file = lr_vars.VarFile.get()
    count = file['Param']['Count']  # число возможных вхождений(4) param в файл(3)
    num = (lr_vars.VarPartNum.get() + 1)  # индекс следующего вхождения(4)
    if num < count:
        # установить вхождение(4)
        lr_vars.VarPartNum.set(num)  # ->> VarLB/VarRB(5)
        return True
    return False  # все входжения param в файл перебраны


def _next_file() -> bool:
    """
    следующей файл(3)
    """
    f = lr_vars.VarFile.get()  # текущий файл
    try:
        index = lr_vars.FilesWithParam.index(f)  # индекс текушего файла(3)
        file = lr_vars.FilesWithParam[index + 1]  # следующий файл
    except IndexError:
        return False  # все файлы перебраны
    else:
        name = file['File']['Name']
        # установить файл(3)
        lr_vars.VarFileName.set(name)  # -> VarFile -> VarFileText ->> VarPartNum(4)
    return True
