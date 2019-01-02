# -*- coding: UTF-8 -*-
# разное

import os

import lr_lib
import lr_lib.etc.excepthook
from lr_lib.core.var import vars as lr_vars
from lr_lib.core_gui.group_param.gp_filter import param_sort

K_FIND = 'Найти'
K_SKIP = 'Пропуск'
K_CANCEL = 'Отменить'
K_CREATE = 'Создать'


def _ask_params(params: [str, ], action: 'lr_lib.gui.action.main_action.ActionWindow', ask=True) -> (int, [str, ]):
    """спросить о создании params, -> 0 - не создавать"""
    old_len_params = len(params)
    if ask:
        pc = '{0} шт.'.format(old_len_params)
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[K_FIND, K_CANCEL, K_SKIP],
            default_key=K_FIND,
            title=pc,
            is_text='\n'.join(params),
            text_before='найти group param',
            text_after=pc,
            parent=action,
        )
        ask = y.ask()

        if ask == K_FIND:
            yt = y.text.split('\n')
            params = param_sort(yt, deny_param_filter=False)
        elif ask == K_SKIP:
            params = []
        else:
            item = (0, [])
            return item

    new_len_params = len(params)
    lr_vars.Logger.info('Имеется {l} ранее созданных param.\nДля создания выбрано/найдено {p}/{_p} param.\n'.format(
        _p=old_len_params, p=new_len_params, l=len(action.web_action.websReport.wrsp_and_param_names)))

    item = (new_len_params, params)
    return item


def responce_files_texts(encoding='utf-8', errors='replace', ) -> iter([(str, str), ]):
    fgen = os.walk(lr_vars.DEFAULT_FILES_FOLDER)
    (dirpath, dirnames, filenames) = next(fgen)
    for file in filenames:
        path = os.path.join(dirpath, file)
        try:
            with open(path, encoding=encoding, errors=errors) as f:
                txt = f.read()

            item = (file, txt)
            yield item
        except Exception as ex:
            lr_lib.etc.excepthook.excepthook(ex)
            continue
    return
