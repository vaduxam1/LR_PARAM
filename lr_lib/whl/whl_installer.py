# -*- coding: UTF-8 -*-
# автоустановка py библиотек офлайн
# импортировать перед импортом всех остальных пользовательских модулей

import sys
import os


def check_py_modules_and_install_whl() -> None:
    """
    whl-офлайн установка модулей, при необходимости, если библиотека не установлена
    """
    try:  # перечислить модули для проверки

        import typing

    except ImportError:  # python < 3.5
        curr_dir = os.getcwd()

        # каталог whl файлов
        whl_dir = os.path.join(curr_dir, 'lr_lib', 'whl', 'install')
        whl_f = os.walk(whl_dir)
        (__root, __folders, whl_files) = next(whl_f)  # файлы

        # pip
        py = os.path.split(sys.executable)
        pip_dir = os.path.join(py[0], 'Scripts')
        pip = os.path.join(pip_dir, 'pip.exe')
        install = '%s install {whl_path}'
        pip_install = (install % pip)

        # pip install whl
        os.chdir(pip_dir)
        try:
            for whl in whl_files:
                whl_path = os.path.join(whl_dir, whl)

                # "c:\python34\Scripts\pip.exe install lr_lib\whl\install\module.whl"
                cmd = pip_install.format(whl_path=whl_path)
                try:
                    os.system(cmd)  # установка whl
                except Exception as ex:
                    print('ImportError {0}'.format(whl), [ex, ex.args])

                continue
        finally:
            os.chdir(curr_dir)
    return
