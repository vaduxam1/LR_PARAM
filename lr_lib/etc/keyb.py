# -*- coding: UTF-8 -*-
# хоткей

import contextlib
import keyboard

import lr_lib.core.var.vars as lr_vars

Err = '''
ImportError keyboard [{}] не работает !
Необходимо установить библиотеку keyboard из cmd.exe:
cd c:\Python36\Scripts\n
 pip install keyboard
'''.format(lr_vars.FIND_PARAM_HOTKEY)


@contextlib.contextmanager
def keyboard_listener() -> None:
    """
    перехват keyboard-hotkey
    не работает в win10 x64: ctypes.ArgumentError: argument 3: <class 'OverflowError'>: int too long to convert
    """
    try:
        keyboard.add_hotkey(lr_vars.FIND_PARAM_HOTKEY, get_param_clipboard_hotkey)
        yield
    finally:
        keyboard.clear_all_hotkeys()
    return


def get_param_clipboard_hotkey() -> None:
    """
    найти {param} из clipboard, по хоткей
    """
    param = lr_vars.Tk.clipboard_get()
    lr_vars.Window.get_files(param=param, clipb=True)
    return
