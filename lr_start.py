# -*- coding: UTF-8 -*-
# v11.6.5 __main__

import os
import sys

from lr_lib.etc.excepthook import full_tb_write
import lr_lib.whl.whl_installer


def set_from_arg(start_py: 'sys.argv[0]') -> str:
    """
    Задать рабочий каталог программы, из полного имени главного запускаемого файла.py, например из sys.argv[0]
    :param start_py: str: 'E:/SCR/proc_ruler/start.py'
    :return: str: 'E:/SCR/proc_ruler'
    Если запускаем скрипт как windows-службу, необходимо сменить домашнюю директорию "окружения", до импорта всех
            пользовательских модулей, на директорию запускаемого скрипта, тк будет стоять директория python.exe.
    Запуск скрипта, как windows-службы, с использованием nssm-2.24:
        Создать: .\nssm-2.24\win64\nssm.exe install vaduxa_process_ruler C:\python37\python.exe E:\proc_ruler\start.py
        Удалить: .\nssm-2.24\win64\nssm.exe remove vaduxa_process_ruler
    """
    (folder, _file) = os.path.split(start_py)  # ('E:/SCR/proc_ruler', 'start.py')
    disk = folder[:3]  # 'C:/'
    # Если текущая домашняя директория, находится на диске('C:/'), отличном от диска задаваемой директории('E:/'):
    os.chdir(disk)  # Сначала необходимо сменить диск.
    os.chdir(folder)  # А уже затем менять домашнюю директорию. Можно и в обратном порядке.
    return folder


set_from_arg(sys.argv[0])  # задать рабочий каталог


def main() -> int:
    """
    Импорт user-библиотек, для проверки доустановки библиокек-python.
    Старт утилиты.
    Сообщение успешного выдода: "Process finished with exit code 0"
    :return: int: OK=0 / Fail=1
    """
    exit_state = False

    # офлайн установка дополнительных py-библиокек, запускать перед импортом остальных.
    lr_lib.whl.whl_installer.check_py_modules_and_install_whl()

    try:  # импорт user-библиотек утилиты, которые возможно потребуют доустановки, дополнительных библиокек-python.
        from lr_lib.main import init
    except ImportError as ex:
        print(lr_lib.whl.whl_installer.ImpErr, file=sys.stdout)
        full_tb_write(ex)

    else:
        try:  # Старт утилиты
            exit_state = init()  # True=OK / None=(если гдето потерялся raise)
        except Exception as ex:
            full_tb_write(ex)

    print('exit_state:', exit_state, file=sys.stdout)
    exit_code = int(not exit_state)  # OK=0 / Fail=1
    return exit_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
