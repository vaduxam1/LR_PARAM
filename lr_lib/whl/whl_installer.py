# -*- coding: UTF-8 -*-
# автоустановка py библиотек офлайн
# запускать перед импортом всех остальных пользовательских модулей

import sys
import os

ImpErr = '''
Возможно python уже установлен, а offline-библиотеки-py-whl не подходят к нему.

Тогда можно поступить любым из путей:
    1) Установить python из "\lr_lib\whl\python-3.4.4.msi". 
        Установить все whl из "\lr_lib\whl\install\",  путем выполнения в cmd: 
            "c:\Python34\Scripts\pip.exe install имя_Файла_модуля.whl", 
                например "pip.exe install typing-3.6.6-py3-none-any.whl". 
        Запустить утилиту, именно с помощью данной версии python.

    2) Доустановить библиотеки из интернета, путем выполнения в cmd: 
            "c:\Python\Scripts\pip.exe install имя_Модуля", 
                например "pip.exe install typing". 
'''

ERR_INSTALL = '''
ERROR: Ошибка офлайн установки файла_whl: {whl}
Установку необходимо запустить вручную(требуется наличие интернета) из консоли cmd, пример:
    "c:\\python34\\Scripts\\pip.exe install имя_Модуля"
имя_Файла_модуля: "typing-3.6.6-py3-none-any.whl" | имя_Модуля: "typing"
'''


def check_py_modules_and_install_whl() -> None:
    """
    whl-офлайн установка библиотек, при необходимости
    """
    try:  # модули, для проверки установлены ли они
        import typing  # в python < 3.5 ее нету
        import keyboard  # вообще не/особо нужен

    except ImportError:  # установить все whl модули, из каталога whl файлов
        curr_dir = os.getcwd()

        # каталог whl файлов
        whl_dir = os.path.join(curr_dir, 'lr_lib', 'whl', 'install')
        whl_f = os.walk(whl_dir)
        (_root, _folders, files_whl) = next(whl_f)  # файлы

        # pip
        (py_path, py_exe) = os.path.split(sys.executable)
        pip_path = os.path.join(py_path, 'Scripts')

        # pip install whl
        for _whl in files_whl:
            whl = os.path.join(whl_dir, _whl)
            bad_state = whl_install(whl, pip_path)
            if bad_state:
                print(ERR_INSTALL.format(whl=whl))
            continue
    return


def whl_install(whl: str, pip_path='') -> int:
    """
    whl-офлайн установка python библиотеки
    :param whl: str: "lr_lib\whl\install\typing-3.6.6-py3-none-any.whl"
    :param pip_path: str: "c:\python34\Scripts\"
    :return: int: 0:OK, AnyOther:Fail
    """
    if pip_path:
        pip = os.path.join(pip_path, 'pip.exe')
        cmd = '{pip} install {whl}'.format(pip=pip, whl=whl)
    else:
        cmd = 'pip.exe install {whl}'.format(whl=whl)

    try:  # c:\python34\Scripts\pip.exe install lr_lib\whl\install\typing-3.6.6-py3-none-any.whl
        state = os.system(cmd)  # установка whl: 0:OK, AnyOther:Fail
    except Exception as ex:
        print('ImportError {cmd}\n'.format(cmd=cmd), [ex, ex.args])
        state = 2
    return state
