# -*- coding: UTF-8 -*-
# v11.6.4 __main__

import sys

from lr_lib.whl.whl_installer import check_py_modules_and_install_whl
check_py_modules_and_install_whl()  # запускать перед импортом остальных

from lr_lib.main import init
from lr_lib.etc.excepthook import full_tb_write


def main(code=False) -> int:
    """
    старт утилиты.
    :return: int: OK = 0 / Fail = 1
        Process finished with exit code 0
    """
    try:
        ec = init()
    except Exception as ex:
        ec = full_tb_write(ex)

    ec = int(not ec)
    return ec


if __name__ == '__main__':
    ec = main()
    sys.exit(ec)
