# -*- coding: UTF-8 -*-
# v11.6.5 __main__

import sys


def main() -> int:
    """
    Импорт user-библиотек, для проверки доустановки библиокек-python.
    Старт утилиты.
    Сообщение успешного выдода: "Process finished with exit code 0"
    :return: int: OK=0 / Fail=1
    """
    ec = False  # exit code

    from lr_lib.etc.excepthook import full_tb_write

    import lr_lib.whl.whl_installer
    # офлайн установка дополнительных py-библиокек, запускать перед импортом остальных.
    lr_lib.whl.whl_installer.check_py_modules_and_install_whl()
    try:  # импорт user-библиотек утилиты, которые возможно потребуют доустановки, дополнительных библиокек-python.
        from lr_lib.main import init
    except ImportError as ex:
        print(lr_lib.whl.whl_installer.ImpErr, file=sys.stdout)
        full_tb_write(ex)  # None
    else:
        try:  # Старт
            ec = init()  # True(OK)/None(если гдето потерялся raise)
        except Exception as ex:
            full_tb_write(ex)

    print('exit code:', ec, file=sys.stdout)
    state = int(not ec)  # OK=0 / Fail=1
    return state


if __name__ == '__main__':
    state = main()
    sys.exit(state)
