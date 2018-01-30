# -*- coding: UTF-8 -*-
# обработка raise

import os
import sys
import traceback

import lr_lib.core.var.vars as lr_vars


def excepthook(*args) -> None:
    """обработка raise: сокращенный стектрейс + исходный код"""
    len_args = len(args)
    if len_args == 1:
        exc_type, exc_val, exc_tb = type(args[0]), args[0], args[0].__traceback__
    elif len_args == 3:
        exc_type, exc_val, exc_tb = args
    else:
        exc_type, exc_val, exc_tb = sys.exc_info()

    full_tb_write(exc_type, exc_val, exc_tb)

    ern = exc_type.__name__
    if lr_vars.Window:
        lr_vars.Window.err_to_widgts(exc_type, exc_val, exc_tb, ern)
    lr_vars.Logger.critical(get_tb(exc_type, exc_val, exc_tb, ern))


def full_tb_write(*args):
    '''логировать полный traceback'''
    if not args:
        exc_type, exc_val, exc_tb = sys.exc_info()
    elif len(args) == 3:
        exc_type, exc_val, exc_tb = args
    elif len(args) == 1:
        exc_ = args[0]
        exc_type, exc_val, exc_tb = exc_.__class__, exc_, exc_.__traceback__
    else:
        raise UserWarning('{e}\n{a}'.format(e=sys.exc_info(), a=list(zip(args, (map(type, args))))))

    # в консоль
    traceback.print_tb(exc_tb)
    # в лог
    with open(lr_vars.logFullName, 'a') as log:
        log.write('\n{0}\n\t>>> traceback.print_tb\n{0}\n'.format(lr_vars.PRINT_SEPARATOR))
        traceback.print_tb(exc_tb, file=log)
        log.write('{t}\n{v}'.format(t=exc_type, v=exc_val))
        log.write('\n{0}\n\t<<< traceback.print_tb\n{0}\n'.format(lr_vars.PRINT_SEPARATOR))

    return exc_type, exc_val, exc_tb


def get_tb(exc_type, exc_val, exc_tb, err_name: str) -> str:
    '''traceback + исходный код'''
    if not exc_tb:
        return '{} {} {}'.format(exc_type, exc_val, exc_tb)
    exc_lines = traceback.format_exception(exc_type, exc_val, exc_tb)

    def get_code(lib='\{}\\'.format(lr_vars.lib_folder)) -> str:
        '''исходный код'''
        line = ''
        for line in reversed(exc_lines):
            if lib in line:
                break
        try:
            fileName = line.split('"')[1]
            lineNum = int(line.split(',')[1].split('line')[-1])
            with open(fileName, errors='replace', encoding='utf-8') as file:
                text = file.read().split('\n')

            left = []
            for line in reversed(text[:lineNum]):
                if line.strip():
                    left.append(line)
                    if len(left) == lr_vars.EHOME:
                        break
            _, f = os.path.split(fileName)
            left[0] = '\n!!! {e} [ {f} : строка {l} ]\n{line}\n'.format(e=err_name, line=left[0], f=f, l=lineNum)
            left.reverse()

            right = []
            for line in text[lineNum:]:
                if line.strip():
                    right.append(line)
                    if len(right) == lr_vars.EEND:
                        break

            code = '{l}\n{r}'.format(l='\n'.join(left), r='\n'.join(right))
            return code
        except Exception as ex:
            return 'неудалось загрузить код файла\n{}'.format(ex)

    tb = ''.join(exc_lines[-1:]).rstrip()
    code = get_code().rstrip()
    return '{tb}\n{s}\n{code}'.format(tb=tb, code=code, s=lr_vars.PRINT_SEPARATOR)
