# -*- coding: UTF-8 -*-
# установка Var файла(3)

import lr_lib
from lr_lib.core.var import vars as lr_vars


def set_file_name(name: str) -> None:
    """
    установка Var имени файла(3)
    """
    file = lr_lib.core.wrsp.files.get_file_with_kwargs(lr_vars.FilesWithParam, Name=name)
    assert file, 'файл "{n}" ({tn}) ненайден. {tf} {f}'.format(n=name, tn=type(name), tf=type(file), f=file)
    lr_vars.VarFile.set(file)
    return


def set_file(file: dict, errors='replace', first_param_part4_num=0) -> None:
    """
    чение файла в lr_vars.VarFileText
    """
    ff = file['File']
    fname = ff['FullName']
    with open(fname, encoding=lr_lib.core.var.etc.vars_other.VarEncode.get(), errors=errors) as f:
        file_text = f.read()
        lr_vars.VarFileText.set(file_text)

    lr_vars.VarPartNum.set(first_param_part4_num)  # выбрать номер варианта вхождения param в файл

    ct = ff['timeCreate']
    if not ct:  # создать статистику, если нет
        lr_lib.core.wrsp.files.set_file_statistic(file, as_text=True)
        # сохранить статистику в AllFiles
        name = ff['Name']
        file_from_allfiles = lr_lib.core.wrsp.files.get_file_with_kwargs(lr_vars.AllFiles, Name=name)
        fp = {k: file[k] for k in file if (k != 'Param')}
        file_from_allfiles.update(fp)
    return
