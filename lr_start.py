# -*- coding: UTF-8 -*-
# v11.6.4 __main__

import sys

from lr_lib.whl.whl_installer  import check_py_modules_and_install_whl
check_py_modules_and_install_whl()  # запускать перед импортом остальных

from lr_lib.main import init
from lr_lib.etc.excepthook import excepthook


def main(code=False) -> int:
    """
    старт утилиты.
    :return: int: OK = 0 / Fail = 1
        Process finished with exit code 0
    """
    try:
        code = init()  # True
    except Exception as ex:
        excepthook(ex)
    finally:
        exit_code = int(not code)  # OK = 0
    return exit_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
