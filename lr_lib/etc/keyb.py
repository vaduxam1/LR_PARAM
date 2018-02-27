# -*- coding: UTF-8 -*-
# хоткей

import contextlib

import lr_lib.core.var.vars as lr_vars

Err = '''
ImportError keyboard [{}] не работает !
Необходимо установить библиотеку keyboard из cmd.exe:
cd c:\Python36\Scripts\n
 pip install keyboard
'''.format(lr_vars.FIND_PARAM_HOTKEY)


@contextlib.contextmanager
def keyboard_listener() -> None:
    """перехват keyboard-hotkey"""
    try:
        import keyboard
    except ImportError:
        lr_vars.Logger.info(Err)
        yield
    else:  # hotkey
        keyboard.add_hotkey(lr_vars.FIND_PARAM_HOTKEY, get_param_clipboard_hotkey)
        yield
        keyboard.clear_all_hotkeys()


def get_param_clipboard_hotkey() -> None:
    """найти {param} из clipboard, по хоткей"""
    param = lr_vars.Tk.clipboard_get()
    lr_vars.Window.get_files(param=param, clipb=True)
