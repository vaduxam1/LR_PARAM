# -*- coding: UTF-8 -*-
# центразизованная  установка lr_vars Var's callback, после импорта всех модулей
# "иерархическая связь" основных Var's друг с другом
# VarParam ->>
#   VarFileName ->
#       VarFile ->
#           VarFileText ->>
#               VarPartNum ->>
#                   VarLB/VarRB ->
#                       VarWrspDict ->>
#                           lr_param.web_reg_save_param

import lr_lib
import lr_lib.core.var.vars as lr_vars
from lr_lib.core.var.var_callback.file_3 import set_file_name, set_file
from lr_lib.core.var.var_callback.part_num import set_param_part_num


def init() -> None:
    """
    установка всех lr_vars.Var's callback
    запускать при старте !
    """
    lr_vars.VarParam.callback_set = lr_lib.core.wrsp.param.get_files_with_param
    lr_vars.VarFileName.callback_set = set_file_name
    lr_vars.VarFile.callback_set = set_file
    lr_vars.VarPartNum.callback_set = set_param_part_num
    return
