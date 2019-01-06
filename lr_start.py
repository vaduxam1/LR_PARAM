# -*- coding: UTF-8 -*-
# v10.5 __main__

import sys

import lr_lib.main


if __name__ == '__main__':
    ex = lr_lib.main.init(excepthook=False)
    sys.exit(ex)
