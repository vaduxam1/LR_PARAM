# -*- coding: UTF-8 -*-
# автоустановка py библиотек офлайн
# запускать перед импортом всех остальных пользовательских модулей

import sys
import os


ERR_INSTALL = '''
ERROR: Ошибка офлайн установки файла_whl: {whl}
Установку необходимо запустить вручную(требуется наличие интернета) из консоли cmd, пример:
    c:\\python34\\Scripts\\pip.exe install имя_модуля
whl_файл: typing-3.6.6-py3-none-any.whl | имя_модуля: typing
'''


def check_py_modules_and_install_whl() -> None:
    """
    whl-офлайн установка библиотек, при необходимости, если они не установлена
    """
    try:  # перечислить модули для проверки

        import typing
        import keyboard

    except ImportError:  # установит все whl модули, из каталога whl файлов
        curr_dir = os.getcwd()

        # каталог whl файлов
        whl_dir = os.path.join(curr_dir, 'lr_lib', 'whl', 'install')
        whl_f = os.walk(whl_dir)
        (__root, __folders, whl_files) = next(whl_f)  # файлы

        # pip
        py_path = os.path.split(sys.executable)
        pip_path = os.path.join(py_path[0], 'Scripts')

        # pip install whl
        os.chdir(pip_path)
        try:
            for whl in whl_files:
                whl_path = os.path.join(whl_dir, whl)
                state = whl_install(whl_path)
                if not state:
                    print(ERR_INSTALL.format(whl=whl_path))
                continue
        finally:
            os.chdir(curr_dir)
    return


def whl_install(whl_path: str, pip_path='', cmd_pip='{pip_path}pip.exe install {whl_path}') -> int:
    """
    whl-офлайн установка python библиотеки
    :param whl_file_path: str: "lr_lib\whl\install\typing-3.6.6-py3-none-any.whl"
    :param cmd_prefix: str: "c:\python34\Scripts\"
    :param cmd_pip: 'pip.exe install {whl}'
    :return: int: 0:OK, AnyOther:Fail
    """
    cmd = cmd_pip.format(pip_path=pip_path, whl_path=whl_path)
    try:  # c:\python34\Scripts\pip.exe install lr_lib\whl\install\typing-3.6.6-py3-none-any.whl
        state = os.system(cmd)  # установка whl: 0:OK, AnyOther:Fail
    except Exception as ex:
        print('ImportError {cmd}\n'.format(cmd=cmd), [ex, ex.args])
        state = 0
    return state
