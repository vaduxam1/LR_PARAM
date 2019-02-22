﻿# -*- coding: UTF-8 -*-
# v11.6.1 __main__

import sys

from lr_lib.main import init
from lr_lib.etc.excepthook import excepthook


def main(exit_code=False) -> int:
    """
    старт утилиты.
    :return: int: OK = 0 / Fail = 1 : Process finished with exit code 0
    """
    try:
        exit_code = init()  # True
    except Exception as ex:
        excepthook(ex)

    exit_code = int(not exit_code)  # OK = 0
    return exit_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
