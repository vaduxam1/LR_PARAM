# -*- coding: UTF-8 -*-
# хоткей

import lr_lib.core.var.vars as lr_vars


def keyboard_listener() -> None:
    '''перехват keyboard-hotkey'''
    try:
        import keyboard
    except ImportError:
        lr_vars.Logger.info('ImportError keyboard [{}] не работает !\nНеобходимо установить библиотеку keyboard из cmd:\n'
                            'cd c:\Python36\Scripts\ \npip install keyboard'.format(lr_vars.FIND_PARAM_HOTKEY))
    else:
        keyboard.add_hotkey(lr_vars.FIND_PARAM_HOTKEY, get_param_hotkey)


def get_param_hotkey() -> None:
    '''найти {param} из clipboard, по хоткей'''
    param = lr_vars.Tk.clipboard_get()
    lr_vars.Window.get_files(param=param)
