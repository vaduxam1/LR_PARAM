﻿# -*- coding: UTF-8 -*-
# v10.0 __main__

import sys

from lr_lib.main import start


if __name__ == '__main__':
    ex = start(with_callback_exception=True)
    sys.exit(ex)