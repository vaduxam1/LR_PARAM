# -*- coding: UTF-8 -*-
# v10.4 __main__

import sys

from lr_lib.main import init


if __name__ == '__main__':
    ex = init(excepthook=True)
    sys.exit(ex)
